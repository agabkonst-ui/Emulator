"""Команда mv: перемещения и переименования узлов VFS только в памяти."""

from .errors import CommandError
from .options import END_OF_OPTIONS, check_letters, is_option
from .paths import PATH_SEPARATOR, ROOT_PATH
from .vfs import VfsDir

MIN_OPERANDS = 2
MOVE_FLAGS = "fn"
FORCE_FLAG = "f"


def parse_move_args(args):
    """Разбирает -f, -n, объединённые флаги и разделитель '--'."""
    operands = []
    overwrite = True
    options_done = False
    for arg in args:
        if options_done or not is_option(arg):
            operands.append(arg)
        elif arg == END_OF_OPTIONS:
            options_done = True
        else:
            for flag in check_letters("mv", arg, MOVE_FLAGS):
                overwrite = flag == FORCE_FLAG
    if len(operands) < MIN_OPERANDS:
        raise CommandError("mv: требуется источник и назначение")
    if any(not path for path in operands):
        raise CommandError("mv: пустой путь недопустим")
    return operands, overwrite


def path_parent(session, path):
    """Находит родительский каталог абсолютного пути и имя узла."""
    parent_path, _separator, name = path.rpartition(PATH_SEPARATOR)
    parent = session.find(parent_path or ROOT_PATH)
    if not isinstance(parent, VfsDir):
        raise CommandError(f"mv: {path}: родительский каталог не найден")
    return parent, name


def check_move_paths(source, target, node):
    """Запрещает перемещение корня, пути в себя и рекурсивный перенос."""
    if source == ROOT_PATH or target == ROOT_PATH:
        raise CommandError("mv: нельзя перемещать или заменять корень")
    if source == target:
        raise CommandError("mv: источник и назначение совпадают")
    if isinstance(node, VfsDir) and target.startswith(source + "/"):
        raise CommandError("mv: нельзя переместить каталог внутрь себя")


def check_replacement(node, existing):
    """Разрешает замену файла либо пустого каталога узлом того же типа."""
    if isinstance(node, VfsDir) != isinstance(existing, VfsDir):
        raise CommandError("mv: типы источника и назначения различаются")
    if isinstance(existing, VfsDir) and existing.children:
        raise CommandError("mv: каталог назначения не пуст")


def relocate_path(path, source, target):
    """Обновляет путь, если он указывает внутрь перемещённого дерева."""
    if path == source or path.startswith(source + PATH_SEPARATOR):
        return target + path[len(source):]
    return path


def move_exact(session, source, target, overwrite):
    """Переносит один узел в точный путь; исходный JSON не записывается."""
    node = session.find(source)
    if node is None:
        raise CommandError(f"mv: {source}: нет такого файла или каталога")
    check_move_paths(source, target, node)
    parent, name = path_parent(session, target)
    existing = parent.children.get(name)
    if existing is not None:
        if not overwrite:
            return
        check_replacement(node, existing)
    source_parent, source_name = path_parent(session, source)
    parent.children[name] = node
    del source_parent.children[source_name]
    session.cwd = relocate_path(session.cwd, source, target)
    session.oldpwd = relocate_path(session.oldpwd, source, target)


def move_source(session, source_arg, destination, into_dir, overwrite):
    """Выбирает конечный путь источника с учётом каталога назначения."""
    source = session.absolute(source_arg)
    if source_arg.endswith(PATH_SEPARATOR):
        if not isinstance(session.find(source), VfsDir):
            raise CommandError(f"mv: {source_arg}: не является каталогом")
    target = destination
    if into_dir:
        name = source.rpartition(PATH_SEPARATOR)[-1]
        target = destination.rstrip(PATH_SEPARATOR) + PATH_SEPARATOR + name
    move_exact(session, source, target, overwrite)


def cmd_mv(args, session):
    """mv [-f|-n] [--] источник... назначение: изменения только в памяти."""
    operands, overwrite = parse_move_args(args)
    destination = session.absolute(operands[-1])
    into_dir = isinstance(session.find(destination), VfsDir)
    if len(operands) > MIN_OPERANDS and not into_dir:
        raise CommandError("mv: несколько источников требуют каталог")
    if operands[-1].endswith(PATH_SEPARATOR) and not into_dir:
        raise CommandError("mv: назначение с '/' должно быть каталогом")
    errors = []
    for source in operands[:-1]:
        try:
            move_source(session, source, destination, into_dir, overwrite)
        except CommandError as error:
            errors.append(str(error))
    if errors:
        raise CommandError("\n".join(errors))
    return None
