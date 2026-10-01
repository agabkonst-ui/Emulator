"""Тесты команд и интерактивного цикла."""

import io
import re
import unittest

from shell_emulator.commands import CommandError, ShellExit, execute
from shell_emulator.repl import build_prompt, repl

PROMPT_PATTERN = r"^.+@.+:~\$ $"
ERROR_EXIT_CODE = 3


def run_session(lines):
    """Прогоняет список строк через REPL, возвращает (код, out, err)."""
    feed = iter(lines)
    def read(_prompt):
        try:
            return next(feed)
        except StopIteration:
            raise EOFError from None

    out, err = io.StringIO(), io.StringIO()
    code = repl(read, out, err)
    return code, out.getvalue(), err.getvalue()


class CommandsTest(unittest.TestCase):
    """Проверки отдельных команд."""

    def test_ls_stub(self):
        """ls выводит своё имя и аргументы."""
        self.assertEqual(execute("ls", ["-l", "/"]), "ls -l /")

    def test_cd_stub(self):
        """cd выводит своё имя и аргумент."""
        self.assertEqual(execute("cd", ["/tmp"]), "cd /tmp")

    def test_cd_too_many_arguments(self):
        """cd с двумя аргументами — ошибка."""
        with self.assertRaises(CommandError):
            execute("cd", ["a", "b"])

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        with self.assertRaises(CommandError):
            execute("foo", [])

    def test_exit_codes(self):
        """exit возвращает код возврата из аргумента."""
        with self.assertRaises(ShellExit) as ctx:
            execute("exit", [str(ERROR_EXIT_CODE)])
        self.assertEqual(ctx.exception.code, ERROR_EXIT_CODE)

    def test_exit_bad_argument(self):
        """exit с нечисловым аргументом — ошибка."""
        with self.assertRaises(CommandError):
            execute("exit", ["abc"])


class ReplTest(unittest.TestCase):
    """Проверки диалога с пользователем."""

    def test_prompt_format(self):
        """Приглашение имеет вид username@hostname:~$."""
        self.assertRegex(build_prompt(), PROMPT_PATTERN)

    def test_session(self):
        """Команды выполняются, ошибки не прерывают работу."""
        code, out, err = run_session(
            ['ls "a b"', "", "foo", "cd 1 2", 'ls "x', "exit"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "ls a b")
        self.assertEqual(len(re.findall("ошибка", err)), 3)

    def test_eof_exits(self):
        """Конец ввода завершает работу эмулятора."""
        code, _out, _err = run_session([])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
