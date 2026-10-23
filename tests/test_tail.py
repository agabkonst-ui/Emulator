"""Тесты команды tail."""

import unittest

from support import make_session, run

ALL_LINES = "один\nдва\nтри\n"


class TailTest(unittest.TestCase):
    """Проверки tail."""

    def setUp(self):
        """Создаёт сеанс с примером VFS."""
        self.session = make_session()

    def tail(self, line):
        """Выполняет команду и возвращает (вывод, ошибки)."""
        return run(self.session, line)

    def test_default_prints_whole_short_file(self):
        """Файл короче 10 строк выводится целиком."""
        out, err = self.tail("tail a.txt")
        self.assertEqual(out, ALL_LINES)
        self.assertEqual(err, "")

    def test_default_ten_lines(self):
        """По умолчанию выводятся 10 последних строк."""
        text = "".join(f"{number}\n" for number in range(1, 16))
        session = make_session({"type": "dir", "children": {
            "long": {"type": "file", "content": text}}})
        out, _err = run(session, "tail long")
        self.assertEqual(out.split(), [str(n) for n in range(6, 16)])

    def test_lines_option_forms(self):
        """-n N, -nN и -N эквивалентны."""
        for line in ("tail -n 2 a.txt", "tail -n2 a.txt", "tail -2 a.txt"):
            out, _err = self.tail(line)
            self.assertEqual(out, "два\nтри\n")

    def test_zero_lines(self):
        """-n 0 ничего не выводит."""
        out, err = self.tail("tail -n 0 a.txt")
        self.assertEqual((out, err), ("", ""))

    def test_from_start(self):
        """-n +N выводит строки начиная с N-й."""
        out, _err = self.tail("tail -n +3 a.txt")
        self.assertEqual(out, "три\n")

    def test_bytes(self):
        """-c N выводит последние N байтов, +N — начиная с N-го."""
        out, _err = self.tail("tail -c 3 ascii.txt")
        self.assertEqual(out, "ef\n")
        out, _err = self.tail("tail -c +5 ascii.txt")
        self.assertEqual(out, "def\n")

    def test_no_trailing_newline(self):
        """Файл без перевода строки в конце читается корректно."""
        out, _err = self.tail("tail -n 1 no_eol.txt")
        self.assertEqual(out, "два\n")

    def test_binary_file_does_not_fail(self):
        """Двоичные данные выводятся без ошибок декодирования."""
        _out, err = self.tail("tail -c 2 bin.dat")
        self.assertEqual(err, "")

    def test_headers_for_several_files(self):
        """Для нескольких файлов выводятся заголовки."""
        out, _err = self.tail("tail -n 1 a.txt no_eol.txt")
        self.assertEqual(
            out, "==> a.txt <==\nтри\n\n==> no_eol.txt <==\nдва\n")

    def test_quiet_and_verbose(self):
        """-q скрывает заголовки, -v показывает их для одного файла."""
        quiet, _err = self.tail("tail -q -n 1 a.txt no_eol.txt")
        verbose, _err = self.tail("tail -v -n 1 a.txt")
        self.assertEqual(quiet, "три\nдва\n")
        self.assertEqual(verbose, "==> a.txt <==\nтри\n")

    def test_end_of_options(self):
        """После '--' аргументы считаются именами файлов."""
        out, _err = self.tail("tail -n 1 -- a.txt")
        self.assertEqual(out, "три\n")

    def test_relative_to_cwd(self):
        """Путь к файлу отсчитывается от текущего каталога."""
        out, _err = run(self.session, "cd d1/d2", "tail deep.txt")
        self.assertEqual(out, "глубоко\n")

    def test_errors(self):
        """Ошибки: нет файла, каталог, нет операнда."""
        for line, fragment in (
                ("tail", "не указан файл"),
                ("tail nope", "нет такого файла"),
                ("tail d1", "это каталог")):
            out, err = self.tail(line)
            self.assertEqual(out, "")
            self.assertIn(fragment, err)

    def test_option_errors(self):
        """Неверное число, неизвестная опция, опция без значения."""
        for line, fragment in (
                ("tail -n x a.txt", "неверное число строк"),
                ("tail -c y a.txt", "неверное число байт"),
                ("tail -z a.txt", "неверная опция"),
                ("tail -n", "требует аргумент")):
            _out, err = self.tail(line)
            self.assertIn(fragment, err)

    def test_partial_output_with_error(self):
        """Для верного файла вывод сохраняется, для неверного — ошибка."""
        out, err = self.tail("tail -n 1 a.txt nope")
        self.assertIn("==> a.txt <==", out)
        self.assertIn("нет такого файла", err)


if __name__ == "__main__":
    unittest.main()
