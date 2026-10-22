"""Тесты виртуальной файловой системы и её команд."""

import io
import json
import os
import tempfile
import unittest

from shell_emulator.cli import VFS_ERROR_CODE, main
from shell_emulator.commands import CommandError, execute
from shell_emulator.session import new_session
from shell_emulator.vfs import (
    VfsDir, VfsError, VfsFile, collect_stats, load_vfs, render_tree)

SAMPLE = {
    "type": "dir",
    "children": {
        "a.txt": {"type": "file", "content": "привет"},
        "bin.dat": {"type": "file", "encoding": "base64",
                    "content": "AAEC"},
        "d1": {"type": "dir", "children": {
            "d2": {"type": "dir", "children": {
                "deep.txt": {"type": "file", "content": "x"}}}}},
    },
}
EXPECTED_TREE = "\n".join([
    "/",
    "|-- a.txt",
    "|-- bin.dat",
    "`-- d1/",
    "    `-- d2/",
    "        `-- deep.txt",
])
BINARY_DATA = bytes([0, 1, 2])


class VfsFileCase(unittest.TestCase):
    """Базовый класс: создаёт временные JSON-файлы."""

    def make_json(self, document):
        """Сохраняет документ (объект или текст) и возвращает путь."""
        text = document if isinstance(document, str) else json.dumps(
            document, ensure_ascii=False)
        handle, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        self.addCleanup(os.remove, path)
        return path


class LoadVfsTest(VfsFileCase):
    """Проверки загрузки VFS из JSON."""

    def test_load_tree(self):
        """Дерево загружается, текст и base64 превращаются в байты."""
        vfs = load_vfs(self.make_json(SAMPLE))
        children = vfs.root.children
        self.assertEqual(children["a.txt"].data, "привет".encode("utf-8"))
        self.assertEqual(children["bin.dat"].data, BINARY_DATA)
        self.assertIsInstance(children["d1"], VfsDir)
        self.assertIsInstance(children["a.txt"], VfsFile)

    def test_minimal(self):
        """Минимальная VFS — пустой корневой каталог."""
        vfs = load_vfs(self.make_json({"type": "dir"}))
        self.assertEqual(vfs.root.children, {})

    def test_stats(self):
        """Статистика считает каталоги, файлы, размер и глубину."""
        stats = collect_stats(load_vfs(self.make_json(SAMPLE)).root)
        self.assertEqual((stats.dirs, stats.files), (2, 3))
        self.assertEqual(stats.depth, 3)

    def test_tree(self):
        """Дерево рисуется с вложенностью в три уровня."""
        vfs = load_vfs(self.make_json(SAMPLE))
        self.assertEqual(render_tree(vfs.root), EXPECTED_TREE)


class LoadErrorsTest(VfsFileCase):
    """Проверки сообщений об ошибках загрузки."""

    def assert_load_error(self, document, fragment):
        """Проверяет, что загрузка падает с ожидаемым сообщением."""
        with self.assertRaises(VfsError) as ctx:
            load_vfs(self.make_json(document))
        self.assertIn(fragment, str(ctx.exception))

    def test_file_not_found(self):
        """Несуществующий файл — ошибка."""
        with self.assertRaises(VfsError) as ctx:
            load_vfs("no/such/vfs.json")
        self.assertIn("файл не найден", str(ctx.exception))

    def test_invalid_json(self):
        """Неверный JSON — ошибка формата."""
        self.assert_load_error('{"type": ', "неверный формат JSON")

    def test_root_must_be_dir(self):
        """Корень-файл недопустим."""
        self.assert_load_error({"type": "file"}, "корень")

    def test_unknown_type(self):
        """Неизвестный тип узла — ошибка."""
        document = {"type": "dir", "children": {"x": {"type": "link"}}}
        self.assert_load_error(document, "неизвестный тип")

    def test_bad_base64(self):
        """Некорректный base64 — ошибка."""
        node = {"type": "file", "encoding": "base64", "content": "!!"}
        document = {"type": "dir", "children": {"x": node}}
        self.assert_load_error(document, "base64")

    def test_bad_name(self):
        """Имя со слэшем недопустимо."""
        node = {"type": "file"}
        document = {"type": "dir", "children": {"a/b": node}}
        self.assert_load_error(document, "недопустимое имя")

    def test_not_an_object(self):
        """Узел, не являющийся объектом, — ошибка."""
        self.assert_load_error([], "JSON-объектом")


class VfsCommandsTest(VfsFileCase):
    """Проверки служебных команд и запуска с VFS."""

    def test_vfs_info_and_tree(self):
        """Команды vfs-info и vfs-tree работают с загруженной VFS."""
        session = new_session(load_vfs(self.make_json(SAMPLE)))
        self.assertIn("файлов: 3", execute("vfs-info", [], session))
        self.assertEqual(execute("vfs-tree", [], session), EXPECTED_TREE)

    def test_commands_need_vfs(self):
        """Без VFS команды сообщают об ошибке."""
        for name in ("vfs-info", "vfs-tree"):
            with self.assertRaises(CommandError):
                execute(name, [], new_session())

    def test_commands_reject_arguments(self):
        """Лишние аргументы — ошибка."""
        session = new_session(load_vfs(self.make_json(SAMPLE)))
        with self.assertRaises(CommandError):
            execute("vfs-tree", ["x"], session)

    def test_main_reports_load_error(self):
        """Ошибка загрузки VFS завершает запуск с кодом 3."""
        out, err = io.StringIO(), io.StringIO()
        code = main(["--vfs", "no/such.json"], input, out, err)
        self.assertEqual(code, VFS_ERROR_CODE)
        self.assertIn("файл не найден", err.getvalue())

    def test_main_loads_vfs(self):
        """При запуске выводится сводка о загруженной VFS."""
        path = self.make_json(SAMPLE)
        feed = iter(["vfs-tree", "exit"])
        out, err = io.StringIO(), io.StringIO()
        code = main(["--vfs", path], lambda _p: next(feed), out, err)
        self.assertEqual(code, 0)
        self.assertIn("VFS загружена: каталогов: 2, файлов: 3",
                      out.getvalue())
        self.assertIn("deep.txt", out.getvalue())


if __name__ == "__main__":
    unittest.main()
