"""Команды эмулятора: заглушки ls и cd, exit и служебные команды VFS."""

from .vfs import collect_stats, render_tree

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды (выводится пользователю)."""


class ShellExit(Exception):
    """Сигнал о завершении работы эмулятора."""

    def __init__(self, code=0):
        """Сохраняет код возврата."""
        super().__init__(code)
        self.code = code


def _stub_output(name, args):
    """Формирует вывод заглушки: имя команды и её аргументы."""
    return " ".join([name, *args])


def cmd_ls(args):
    """Заглушка ls: печатает своё имя и аргументы."""
    return _stub_output("ls", args)


def cmd_cd(args):
    """Заглушка cd: печатает своё имя и аргументы (не более одного)."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: слишком много аргументов")
    return _stub_output("cd", args)


def cmd_exit(args):
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


def cmd_vfs_info(args, vfs):
    """Служебная команда: сведения о загруженной VFS."""
    check_no_args("vfs-info", args)
    require_vfs("vfs-info", vfs)
    stats = collect_stats(vfs.root)
    return "\n".join([
        f"источник: {vfs.source}",
        f"каталогов: {stats.dirs}",
        f"файлов: {stats.files}",
        f"размер: {stats.size} байт",
        f"глубина: {stats.depth}",
    ])


def cmd_vfs_tree(args, vfs):
    """Служебная команда: дерево каталогов и файлов VFS."""
    check_no_args("vfs-tree", args)
    require_vfs("vfs-tree", vfs)
    return render_tree(vfs.root)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}

VFS_COMMANDS = {
    "vfs-info": cmd_vfs_info,
    "vfs-tree": cmd_vfs_tree,
}


def execute(name, args, vfs=None):
    """Выполняет команду и возвращает её вывод (строку или None)."""
    handler = COMMANDS.get(name)
    if handler is not None:
        return handler(args)
    vfs_handler = VFS_COMMANDS.get(name)
    if vfs_handler is not None:
        return vfs_handler(args, vfs)
    raise CommandError(f"{name}: команда не найдена")
