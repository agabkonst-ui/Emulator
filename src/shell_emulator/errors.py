"""Исключения эмулятора: ошибка команды и сигнал о завершении."""


class CommandError(Exception):
    """Ошибка выполнения команды (выводится пользователю).

    Необязательный output хранит вывод, полученный до ошибки: так
    команды вроде ls и tail показывают результат для верных аргументов.
    """

    def __init__(self, message, output=None):
        """Сохраняет сообщение об ошибке и частичный вывод."""
        super().__init__(message)
        self.output = output


class ShellExit(Exception):
    """Сигнал о завершении работы эмулятора."""

    def __init__(self, code=0):
        """Сохраняет код возврата."""
        super().__init__(code)
        self.code = code
