"""Реестр команд эмулятора: ls, cd, pwd, history, tail, exit и служебные."""

from .errors import CommandError, ShellExit
from .fs_commands import cmd_cd, cmd_ls, cmd_pwd
from .history import cmd_history
from .tail import cmd_tail
from .vfs import collect_stats, render_tree

MAX_EXIT_ARGS = 1


def cmd_exit(args, _session):
    """Завершает работу эмулятора с необязательным кодом возврата."""
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("exit: слишком много аргументов")
    if not args:
        raise ShellExit(0)
    try:
        code = int(args[0])
    except ValueError:
        raise CommandError(
            f"exit: {args[0]}: требуется числовой аргумент") from None
    raise ShellExit(code)


def check_no_args(name, args):
    """Проверяет, что служебной команде не переданы аргументы."""
    if args:
        raise CommandError(f"{name}: аргументы не поддерживаются")


def require_vfs(name, vfs):
    """Проверяет, что VFS загружена, иначе сообщает об ошибке."""
    if vfs is None:
        raise CommandError(f"{name}: VFS не загружена (укажите --vfs)")


def cmd_vfs_info(args, session):
    """Служебная команда: сведения о загруженной VFS."""
    check_no_args("vfs-info", args)
    require_vfs("vfs-info", session.vfs)
    vfs = session.vfs
    stats = collect_stats(vfs.root)
    return "\n".join([
        f"источник: {vfs.source}",
        f"каталогов: {stats.dirs}",
        f"файлов: {stats.files}",
        f"размер: {stats.size} байт",
        f"глубина: {stats.depth}",
    ])


def cmd_vfs_tree(args, session):
    """Служебная команда: дерево каталогов и файлов VFS."""
    check_no_args("vfs-tree", args)
    require_vfs("vfs-tree", session.vfs)
    return render_tree(session.vfs.root)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "history": cmd_history,
    "tail": cmd_tail,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
    "vfs-tree": cmd_vfs_tree,
}


def execute(name, args, session):
    """Выполняет команду и возвращает её вывод (строку или None)."""
    handler = COMMANDS.get(name)
    if handler is None:
        raise CommandError(f"{name}: команда не найдена")
    return handler(args, session)
