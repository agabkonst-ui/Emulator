"""Тесты параметров командной строки."""

import contextlib
import io
import unittest

from shell_emulator.config import NOT_SET, format_debug, parse_args

ARGPARSE_ERROR_CODE = 2


class ParseArgsTest(unittest.TestCase):
    """Проверки разбора параметров."""

    def test_defaults(self):
        """Без параметров значения не заданы."""
        args = parse_args([])
        self.assertIsNone(args.vfs)
        self.assertIsNone(args.script)

    def test_all_params(self):
        """Оба параметра разбираются."""
        args = parse_args(["--vfs", "a/vfs.json", "--script", "s.txt"])
        self.assertEqual(args.vfs, "a/vfs.json")
        self.assertEqual(args.script, "s.txt")

    def test_unknown_param(self):
        """Неизвестный параметр завершает разбор с кодом 2."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                parse_args(["--bogus"])
        self.assertEqual(ctx.exception.code, ARGPARSE_ERROR_CODE)

    def test_missing_value(self):
        """Параметр без значения — ошибка."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["--vfs"])


class FormatDebugTest(unittest.TestCase):
    """Проверки отладочного вывода."""

    def test_lists_every_param(self):
        """Выводятся все параметры, незаданные помечаются."""
        lines = format_debug(parse_args(["--vfs", "v.json"]))
        text = "\n".join(lines)
        self.assertIn("script = " + NOT_SET, text)
        self.assertIn("vfs = v.json", text)


if __name__ == "__main__":
    unittest.main()
