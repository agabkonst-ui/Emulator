"""Тесты команд и интерактивного цикла."""

import io
import re
import unittest

from shell_emulator.commands import CommandError, ShellExit, execute
from shell_emulator.repl import build_prompt, repl
from shell_emulator.session import new_session

PROMPT_PATTERN = r"^.+@.+:/\$ $"
PROMPT_IN_DIR_PATTERN = r"^.+@.+:/home/user\$ $"
ERROR_EXIT_CODE = 3


def run_session(lines):
    """Прогоняет список строк через REPL, возвращает (код, out, err)."""
    feed = iter(lines)
    def read(_prompt):
        """Подаёт заготовленные строки вместо ввода пользователя."""
        try:
            return next(feed)
        except StopIteration:
            raise EOFError from None

    out, err = io.StringIO(), io.StringIO()
    code = repl(read, out, err)
    return code, out.getvalue(), err.getvalue()


class CommandsTest(unittest.TestCase):
    """Проверки отдельных команд."""

    def setUp(self):
        """Создаёт пустой сеанс без VFS."""
        self.session = new_session()

    def test_pwd(self):
        """pwd выводит текущий каталог."""
        self.assertEqual(execute("pwd", [], self.session), "/")

    def test_cd_too_many_arguments(self):
        """cd с двумя аргументами — ошибка."""
        with self.assertRaises(CommandError):
            execute("cd", ["a", "b"], self.session)

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        with self.assertRaises(CommandError):
            execute("foo", [], self.session)

    def test_exit_codes(self):
        """exit возвращает код возврата из аргумента."""
        with self.assertRaises(ShellExit) as ctx:
            execute("exit", [str(ERROR_EXIT_CODE)], self.session)
        self.assertEqual(ctx.exception.code, ERROR_EXIT_CODE)

    def test_exit_bad_argument(self):
        """exit с нечисловым аргументом — ошибка."""
        with self.assertRaises(CommandError):
            execute("exit", ["abc"], self.session)


class ReplTest(unittest.TestCase):
    """Проверки диалога с пользователем."""

    def test_prompt_format(self):
        """Приглашение имеет вид username@hostname:/$."""
        self.assertRegex(build_prompt(), PROMPT_PATTERN)

    def test_prompt_shows_directory(self):
        """В приглашении показывается текущий каталог."""
        self.assertRegex(build_prompt("/home/user"), PROMPT_IN_DIR_PATTERN)

    def test_session(self):
        """Команды выполняются, ошибки не прерывают работу."""
        code, out, err = run_session(
            ["pwd", "", "foo", "cd 1 2", 'ls "x', "exit"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "/")
        self.assertEqual(len(re.findall("ошибка", err)), 3)

    def test_eof_exits(self):
        """Конец ввода завершает работу эмулятора."""
        code, _out, _err = run_session([])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
