"""Тесты стартового скрипта и запуска эмулятора."""

import io
import os
import tempfile
import unittest

from shell_emulator.cli import SCRIPT_ERROR_CODE, main
from shell_emulator.commands import ShellExit
from shell_emulator.script import is_skipped, load_script, run_script

PROMPT = "u@h:~$ "
EXIT_CODE = 5


def run_main(argv, stdin_lines=()):
    """Запускает main с заданным вводом, возвращает (код, out, err)."""
    feed = iter(stdin_lines)

    def read(_prompt):
        """Подаёт заготовленные строки вместо ввода пользователя."""
        try:
            return next(feed)
        except StopIteration:
            raise EOFError from None

    out, err = io.StringIO(), io.StringIO()
    code = main(argv, read, out, err)
    return code, out.getvalue(), err.getvalue()


class ScriptFileCase(unittest.TestCase):
    """Базовый класс: создаёт временные файлы скриптов."""

    def make_script(self, text):
        """Сохраняет текст во временный файл и возвращает путь."""
        handle, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        self.addCleanup(os.remove, path)
        return path


class RunScriptTest(unittest.TestCase):
    """Проверки выполнения строк скрипта."""

    def test_skipped_lines(self):
        """Пустые строки и комментарии пропускаются."""
        self.assertTrue(is_skipped("   "))
        self.assertTrue(is_skipped("  # comment"))
        self.assertFalse(is_skipped("ls"))

    def test_echo_and_errors(self):
        """Вводится и выводится диалог, ошибочные строки пропускаются."""
        out, err = io.StringIO(), io.StringIO()
        run_script(["ls a", "foo", "# note", "", "cd 1 2", "cd b"],
                   PROMPT, out, err)
        self.assertEqual(
            out.getvalue(),
            f"{PROMPT}ls a\nls a\n{PROMPT}foo\n{PROMPT}cd 1 2\n"
            f"{PROMPT}cd b\ncd b\n")
        self.assertEqual(err.getvalue().count("ошибка"), 2)

    def test_exit_stops_script(self):
        """Команда exit прерывает скрипт кодом возврата."""
        out, err = io.StringIO(), io.StringIO()
        with self.assertRaises(ShellExit) as ctx:
            run_script([f"exit {EXIT_CODE}", "ls"], PROMPT, out, err)
        self.assertEqual(ctx.exception.code, EXIT_CODE)
        self.assertNotIn("ls", out.getvalue().split("exit")[-1])


class MainTest(ScriptFileCase):
    """Проверки запуска эмулятора с параметрами."""

    def test_debug_output_without_params(self):
        """Параметры печатаются даже если не заданы."""
        code, out, _err = run_main([])
        self.assertEqual(code, 0)
        self.assertIn("[отладка] Параметры запуска:", out)
        self.assertIn("vfs = (не задан)", out)

    def test_debug_output_with_params(self):
        """Заданные параметры печатаются в отладочном выводе."""
        path = self.make_script("exit\n")
        _code, out, _err = run_main(["--vfs", "/data/vfs", "--script", path])
        self.assertIn("vfs = /data/vfs", out)
        self.assertIn(f"script = {path}", out)

    def test_script_then_interactive(self):
        """После скрипта без exit начинается интерактивный режим."""
        path = self.make_script("ls x\n")
        code, out, _err = run_main(["--script", path], ["cd y"])
        self.assertEqual(code, 0)
        self.assertIn("ls x", out)
        self.assertIn("cd y", out)

    def test_script_exit_code(self):
        """Код exit из скрипта становится кодом возврата."""
        path = self.make_script(f"exit {EXIT_CODE}\n")
        code, _out, _err = run_main(["--script", path])
        self.assertEqual(code, EXIT_CODE)

    def test_missing_script(self):
        """Отсутствующий скрипт — ошибка с кодом 2."""
        code, _out, err = run_main(["--script", "no/such/file.txt"])
        self.assertEqual(code, SCRIPT_ERROR_CODE)
        self.assertIn("ошибка", err)

    def test_load_script_strips_bom(self):
        """BOM в начале скрипта не попадает в первую команду."""
        handle, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(handle, "wb") as stream:
            stream.write(b"\xef\xbb\xbfls\r\nexit\r\n")
        self.addCleanup(os.remove, path)
        self.assertEqual(load_script(path), ["ls", "exit"])


if __name__ == "__main__":
    unittest.main()
