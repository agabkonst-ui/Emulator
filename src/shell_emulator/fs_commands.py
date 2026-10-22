"""Команды навигации по VFS: ls, cd и pwd."""

from .errors import CommandError
from .options import END_OF_OPTIONS, is_option, parse_flags
from .paths import CURRENT_DIR, PARENT_DIR, ROOT_PATH, normalize_path
from .vfs import VfsDir, find_node

ALL_FLAG = "a"
LONG_FLAG = "l"
REVERSE_FLAG = "r"
LS_FLAGS = ALL_FLAG + LONG_FLAG + REVERSE_FLAG
PWD_FLAGS = "LP"
MAX_CD_ARGS = 1
SINGLE_OPERAND = 1
PREVIOUS_DIR = "-"
KIND_DIR = "d"
KIND_FILE = "-"
DIR_SIZE = 0
SIZE_WIDTH = 8
BLOCK_SEPARATOR = "\n\n"
LINE_SEPARATOR = "\n"


def not_found(name, path):
    """Сообщение о том, что путь в VFS не существует."""
    return f"{name}: {path}: нет такого файла или каталога"


def entry_line(name, node, long_format):
    """Формирует строку ls для узла: имя или длинный формат."""
    if not long_format:
        return name
    if isinstance(node, VfsDir):
        kind, size = KIND_DIR, DIR_SIZE
    else:
        kind, size = KIND_FILE, len(node.data)
    return f"{kind} {size:>{SIZE_WIDTH}} {name}"


def dir_entries(session, path, node, flags):
    """Возвращает отсортированные пары (имя, узел) каталога.

    Скрытые имена (с точкой) показываются только с флагом -a, вместе с
    записями '.' и '..'. Флаг -r меняет порядок на обратный.
    """
    entries = dict(node.children)
    if ALL_FLAG in flags:
        parent = find_node(session.root, normalize_path(path, PARENT_DIR))
        entries[CURRENT_DIR] = node
        entries[PARENT_DIR] = parent
    else:
        entries = {name: child for name, child in entries.items()
                   if not name.startswith(CURRENT_DIR)}
    items = sorted(entries.items(),
                   key=lambda item: (item[0].lower(), item[0]))
    if REVERSE_FLAG in flags:
        items.reverse()
    return items


def classify_operands(session, operands):
    """Делит операнды ls на файлы, каталоги и сообщения об ошибках."""
    files, dirs, errors = [], [], []
    for operand in operands:
        node = session.find(operand)
        if node is None:
            errors.append(not_found("ls", operand))
        elif isinstance(node, VfsDir):
            dirs.append((operand, node))
        else:
            files.append((operand, node))
    return files, dirs, errors


def list_dir_block(session, operand, node, flags, with_header):
    """Строит текст списка каталога, при необходимости с заголовком."""
    long_format = LONG_FLAG in flags
    lines = [f"{operand}:"] if with_header else []
    path = session.absolute(operand)
    for name, child in dir_entries(session, path, node, flags):
        lines.append(entry_line(name, child, long_format))
    return LINE_SEPARATOR.join(lines)


def cmd_ls(args, session):
    """ls [-a] [-l] [-r] [путь...]: содержимое каталогов и файлы VFS."""
    flags, operands = parse_flags("ls", args, LS_FLAGS)
    operands = operands or [CURRENT_DIR]
    files, dirs, errors = classify_operands(session, operands)
    long_format = LONG_FLAG in flags
    blocks = [LINE_SEPARATOR.join(
        entry_line(name, node, long_format) for name, node in sorted(files))]
    with_header = len(operands) > SINGLE_OPERAND
    blocks.extend(list_dir_block(session, operand, node, flags, with_header)
                  for operand, node in dirs)
    output = BLOCK_SEPARATOR.join(block for block in blocks if block)
    if errors:
        raise CommandError(LINE_SEPARATOR.join(errors), output or None)
    return output


def cd_target(args, session):
    """Определяет путь для cd: без аргумента — корень, '-' — прежний."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: слишком много аргументов")
    target = args[0] if args else ROOT_PATH
    if target == END_OF_OPTIONS:
        return ROOT_PATH
    if is_option(target):
        raise CommandError(f"cd: {target}: неверная опция")
    return session.oldpwd if target == PREVIOUS_DIR else target


def cmd_cd(args, session):
    """cd [путь | -]: смена текущего каталога VFS.

    'cd' без аргумента переходит в корень, 'cd -' — в предыдущий
    каталог (и печатает его путь).
    """
    target = cd_target(args, session)
    node = session.find(target)
    if node is None:
        raise CommandError(not_found("cd", target))
    if not isinstance(node, VfsDir):
        raise CommandError(f"cd: {target}: не является каталогом")
    session.oldpwd = session.cwd
    session.cwd = session.absolute(target)
    return session.cwd if args and args[0] == PREVIOUS_DIR else None


def cmd_pwd(args, session):
    """pwd [-L] [-P]: печатает путь текущего каталога VFS."""
    _flags, operands = parse_flags("pwd", args, PWD_FLAGS)
    if operands:
        raise CommandError("pwd: слишком много аргументов")
    return session.cwd
