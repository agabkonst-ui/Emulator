"""Команды эмулятора: заглушки ls и cd, а также exit."""

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


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute(name, args):
    """Выполняет команду и возвращает её вывод (строку или None)."""
    handler = COMMANDS.get(name)
    if handler is None:
        raise CommandError(f"{name}: команда не найдена")
    return handler(args)
