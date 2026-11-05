"""Тесты этапа 5 на исходной архитектуре проекта этапа 4."""

import copy
import tempfile
import unittest
from pathlib import Path

from support import make_session, run
from shell_emulator.session import new_session
from shell_emulator.vfs import VfsDir, load_vfs

EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples/vfs/deep.json"


class MoveTest(unittest.TestCase):
    """Проверки перемещений, режимов замены и ошибок."""

    def setUp(self):
        """Создаёт независимый сеанс для каждой проверки."""
        self.session = make_session()

    def test_rename_preserves_bytes(self):
        """Переименование сохраняет содержимое, удаляет старое имя."""
        original = self.session.find("a.txt").data
        _out, err = run(self.session, "mv a.txt renamed.txt")
        self.assertEqual(err, "")
        self.assertIsNone(self.session.find("a.txt"))
        self.assertEqual(self.session.find("renamed.txt").data, original)

    def test_move_file_into_directory(self):
        """Файл попадает в существующий каталог под прежним именем."""
        _out, err = run(self.session, "mv a.txt empty/")
        self.assertEqual(err, "")
        self.assertIsNotNone(self.session.find("empty/a.txt"))

    def test_directory_rename_and_move(self):
        """Вложенное дерево сохраняется после переименования и переноса."""
        _out, err = run(self.session, "mv d1 tree", "mv tree empty")
        self.assertEqual(err, "")
        self.assertIsNotNone(self.session.find("empty/tree/d2/deep.txt"))

    def test_current_and_previous_directory_follow_tree(self):
        """cwd и oldpwd обновляются, поэтому cd - продолжает работать."""
        _out, err = run(self.session, "cd d1/d2", "cd /empty",
                        "mv /d1 /tree", "cd -", "pwd")
        self.assertEqual(err, "")
        self.assertEqual(self.session.cwd, "/tree/d2")
        run(self.session, "mv /tree /renamed")
        self.assertEqual(self.session.cwd, "/renamed/d2")

    def test_default_and_force_overwrite(self):
        """По умолчанию и с -f существующий файл заменяется."""
        for option in ("", "-f "):
            with self.subTest(option=option):
                session = make_session()
                expected = session.find("a.txt").data
                _out, err = run(session, f"mv {option}a.txt ascii.txt")
                self.assertEqual(err, "")
                self.assertEqual(session.find("ascii.txt").data, expected)
                self.assertIsNone(session.find("a.txt"))

    def test_no_clobber(self):
        """-n пропускает существующую цель и сохраняет оба файла."""
        before = copy.deepcopy(self.session.root)
        _out, err = run(self.session, "mv -n a.txt ascii.txt")
        self.assertEqual(err, "")
        self.assertEqual(self.session.root, before)

    def test_combined_flags_last_wins(self):
        """Для -fn и -nf действует последняя буква."""
        run(self.session, "mv -fn a.txt ascii.txt")
        self.assertIsNotNone(self.session.find("a.txt"))
        run(self.session, "mv -nf a.txt ascii.txt")
        self.assertIsNone(self.session.find("a.txt"))

    def test_separate_flags_last_wins(self):
        """Порядок отдельных -f и -n также сохраняется."""
        run(self.session, "mv -f -n a.txt ascii.txt")
        self.assertIsNotNone(self.session.find("a.txt"))
        run(self.session, "mv -n -f a.txt ascii.txt")
        self.assertIsNone(self.session.find("a.txt"))

    def test_multiple_sources(self):
        """Несколько файлов перемещаются в общий каталог."""
        _out, err = run(self.session, "mv a.txt ascii.txt empty")
        self.assertEqual(err, "")
        self.assertIsNotNone(self.session.find("empty/a.txt"))
        self.assertIsNotNone(self.session.find("empty/ascii.txt"))

    def test_partial_failure_continues(self):
        """Ошибка источника не мешает переносу остальных источников."""
        _out, err = run(self.session, "mv missing a.txt empty")
        self.assertIn("нет такого файла", err)
        self.assertIsNotNone(self.session.find("empty/a.txt"))

    def test_quoted_and_relative_paths(self):
        """Кавычки, абсолютные и относительные пути совместимы."""
        _out, err = run(self.session, 'mv a.txt "with spaces.txt"',
                        "cd d1", 'mv "../with spaces.txt" /empty/new.txt')
        self.assertEqual(err, "")
        self.assertIsNotNone(self.session.find("/empty/new.txt"))

    def test_end_of_options_and_binary(self):
        """-- разрешает дефис в имени; двоичные байты сохраняются."""
        original = self.session.find("bin.dat").data
        _out, err = run(self.session, "mv bin.dat ./-binary",
                        "mv -- -binary empty")
        self.assertEqual(err, "")
        self.assertEqual(self.session.find("empty/-binary").data, original)

    def test_invalid_operations_are_atomic(self):
        """Ошибки одиночного переноса не меняют дерево или пути сеанса."""
        commands = (
            "mv", "mv a.txt", "mv -z a.txt empty", 'mv "" empty',
            'mv a.txt ""', "mv missing empty", "mv a.txt a.txt",
            "mv / empty", "mv d1 d1/d2", "mv d1 ascii.txt",
            "mv a.txt missing/new", "mv a.txt missing/",
            "mv a.txt/ empty", "mv a.txt ascii.txt nowhere",
            "mv a.txt ascii.txt/new", "mv d1 .",
        )
        for command in commands:
            with self.subTest(command=command):
                before = copy.deepcopy(self.session)
                _out, err = run(self.session, command)
                self.assertIn("ошибка:", err)
                self.assertEqual(self.session.root, before.root)
                self.assertEqual(self.session.cwd, before.cwd)
                self.assertEqual(self.session.oldpwd, before.oldpwd)

    def test_empty_directory_replacement(self):
        """Внутри назначения одноимённый пустой каталог заменяется."""
        self.session.find("empty").children["d1"] = VfsDir()
        _out, err = run(self.session, "mv d1 empty")
        self.assertEqual(err, "")
        self.assertIsNotNone(self.session.find("empty/d1/d2/deep.txt"))

    def test_nonempty_directory_replacement_rejected(self):
        """Непустой каталог назначения нельзя заменить."""
        self.session.find("empty").children["d1"] = VfsDir({"x": VfsDir()})
        before = copy.deepcopy(self.session.root)
        _out, err = run(self.session, "mv d1 empty")
        self.assertIn("не пуст", err)
        self.assertEqual(self.session.root, before)

    def test_file_cannot_replace_directory(self):
        """Файл не заменяет одноимённый каталог внутри назначения."""
        self.session.find("empty").children["a.txt"] = VfsDir()
        _out, err = run(self.session, "mv a.txt empty")
        self.assertIn("типы", err)
        self.assertIsNotNone(self.session.find("a.txt"))

    def test_missing_vfs(self):
        """Без VFS команда сообщает об отсутствии источника."""
        _out, err = run(new_session(), "mv absent target")
        self.assertIn("нет такого файла", err)

    def test_json_never_written_and_reload_resets(self):
        """Сравнивает байты JSON и восстановление VFS после перезапуска."""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "vfs.json"
            path.write_bytes(EXAMPLE_PATH.read_bytes())
            before = path.read_bytes()
            session = new_session(load_vfs(str(path)))
            source = next(iter(session.root.children))
            _out, err = run(session, f"mv {source} renamed")
            self.assertEqual(err, "")
            self.assertEqual(path.read_bytes(), before)
            fresh = new_session(load_vfs(str(path)))
            self.assertIsNotNone(fresh.find(source))
            self.assertIsNone(fresh.find("renamed"))


if __name__ == "__main__":
    unittest.main()
