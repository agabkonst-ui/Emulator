"""Тесты команд ls, cd и pwd."""

import unittest

from support import make_session, run
from shell_emulator.session import new_session

LONG_DIR = "d        0 d1"
LONG_FILE = "-        3 bin.dat"


class LsTest(unittest.TestCase):
    """Проверки ls."""

    def setUp(self):
        """Создаёт сеанс с примером VFS."""
        self.session = make_session()

    def test_plain_listing_hides_dot_names(self):
        """Без флагов скрытые имена не показываются, порядок по имени."""
        out, err = run(self.session, "ls")
        self.assertEqual(
            out.split(),
            ["a.txt", "ascii.txt", "bin.dat", "d1", "empty", "no_eol.txt"])
        self.assertEqual(err, "")

    def test_all_flag_adds_hidden_and_dots(self):
        """Флаг -a показывает скрытые файлы, '.' и '..'."""
        out, _err = run(self.session, "ls -a")
        self.assertEqual(out.split()[:3], [".", "..", ".hidden"])

    def test_reverse_flag(self):
        """Флаг -r выводит имена в обратном порядке."""
        out, _err = run(self.session, "ls -r")
        self.assertEqual(out.split()[0], "no_eol.txt")

    def test_long_format(self):
        """Флаг -l показывает тип и размер."""
        out, _err = run(self.session, "ls -l")
        self.assertIn(LONG_DIR, out.splitlines())
        self.assertIn(LONG_FILE, out.splitlines())

    def test_combined_flags(self):
        """Флаги можно объединять: -la."""
        out, _err = run(self.session, "ls -la")
        self.assertIn("d        0 ..", out.splitlines())

    def test_path_argument(self):
        """Путь к каталогу — относительный и абсолютный."""
        relative, _err = run(self.session, "ls d1")
        absolute, _err = run(self.session, "ls /d1/d2")
        self.assertEqual(relative.split(), ["d2"])
        self.assertEqual(absolute.split(), ["deep.txt"])

    def test_file_argument(self):
        """Для файла ls печатает его имя."""
        out, _err = run(self.session, "ls d1/d2/deep.txt")
        self.assertEqual(out.strip(), "d1/d2/deep.txt")

    def test_several_paths_have_headers(self):
        """Несколько путей: файлы, затем каталоги с заголовками."""
        out, _err = run(self.session, "ls d1 a.txt empty")
        self.assertEqual(out, "a.txt\n\nd1:\nd2\n\nempty:\n")

    def test_missing_path_reports_error_and_keeps_output(self):
        """Ошибка по одному пути не скрывает вывод по остальным."""
        out, err = run(self.session, "ls d1 missing")
        self.assertIn("d2", out)
        self.assertIn("ls: missing: нет такого файла", err)

    def test_unknown_flag(self):
        """Неизвестный флаг — ошибка."""
        out, err = run(self.session, "ls -z")
        self.assertEqual(out, "")
        self.assertIn("неверная опция", err)

    def test_empty_vfs_session(self):
        """Без VFS ls работает с пустым корнем."""
        out, err = run(new_session(), "ls", "ls -a")
        self.assertEqual(out.split(), [".", ".."])
        self.assertEqual(err, "")


class CdTest(unittest.TestCase):
    """Проверки cd и pwd."""

    def setUp(self):
        """Создаёт сеанс с примером VFS."""
        self.session = make_session()

    def test_pwd_at_start(self):
        """В начале работы текущий каталог — корень."""
        out, _err = run(self.session, "pwd")
        self.assertEqual(out, "/\n")

    def test_cd_relative_and_absolute(self):
        """Переходы по относительному и абсолютному пути."""
        run(self.session, "cd d1/d2")
        self.assertEqual(self.session.cwd, "/d1/d2")
        run(self.session, "cd /empty")
        self.assertEqual(self.session.cwd, "/empty")

    def test_cd_parent_and_dot(self):
        """'..' и '.' в путях."""
        run(self.session, "cd d1/d2", "cd ../.", "cd ..")
        self.assertEqual(self.session.cwd, "/")

    def test_relative_ls_after_cd(self):
        """ls работает относительно нового каталога."""
        out, _err = run(self.session, "cd d1", "ls", "pwd")
        self.assertEqual(out, "d2\n/d1\n")

    def test_cd_without_argument_goes_to_root(self):
        """cd без аргумента переходит в корень."""
        run(self.session, "cd d1", "cd")
        self.assertEqual(self.session.cwd, "/")

    def test_cd_dash_swaps_directories(self):
        """cd - возвращает в прежний каталог и печатает его."""
        out, _err = run(self.session, "cd d1", "cd -", "cd -")
        self.assertEqual(out, "/\n/d1\n")

    def test_cd_missing(self):
        """Несуществующий каталог — ошибка, каталог не меняется."""
        _out, err = run(self.session, "cd nowhere")
        self.assertIn("нет такого файла", err)
        self.assertEqual(self.session.cwd, "/")

    def test_cd_to_file(self):
        """cd в файл — ошибка."""
        _out, err = run(self.session, "cd a.txt")
        self.assertIn("не является каталогом", err)

    def test_cd_errors(self):
        """Лишние аргументы и неизвестная опция — ошибки."""
        _out, err = run(self.session, "cd a b", "cd -x")
        self.assertIn("слишком много аргументов", err)
        self.assertIn("неверная опция", err)

    def test_pwd_extra_argument(self):
        """pwd с операндом — ошибка."""
        _out, err = run(self.session, "pwd x")
        self.assertIn("слишком много аргументов", err)

    def test_pwd_flags(self):
        """pwd принимает -L и -P."""
        out, _err = run(self.session, "pwd -L", "pwd -P")
        self.assertEqual(out, "/\n/\n")


if __name__ == "__main__":
    unittest.main()
