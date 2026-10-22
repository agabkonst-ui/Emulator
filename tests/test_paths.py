"""Тесты нормализации путей VFS."""

import unittest

from shell_emulator.paths import join_parts, normalize_path, split_path


class PathsTest(unittest.TestCase):
    """Проверки разбора и нормализации путей."""

    def test_split_skips_empty_and_dot(self):
        """Пустые части и '.' отбрасываются."""
        self.assertEqual(split_path("/a//b/./c/"), ["a", "b", "c"])

    def test_join_root(self):
        """Пустой список имён даёт корень."""
        self.assertEqual(join_parts([]), "/")

    def test_absolute_path_ignores_cwd(self):
        """Абсолютный путь не зависит от текущего каталога."""
        self.assertEqual(normalize_path("/x/y", "/a/b"), "/a/b")

    def test_relative_path(self):
        """Относительный путь отсчитывается от cwd."""
        self.assertEqual(normalize_path("/x", "y/z"), "/x/y/z")

    def test_parent_directory(self):
        """'..' поднимается на уровень выше."""
        self.assertEqual(normalize_path("/x/y", "../z"), "/x/z")

    def test_parent_of_root_is_root(self):
        """'..' в корне остаётся в корне."""
        self.assertEqual(normalize_path("/", "../.."), "/")

    def test_empty_path_is_cwd(self):
        """Пустой путь означает текущий каталог."""
        self.assertEqual(normalize_path("/x", ""), "/x")


if __name__ == "__main__":
    unittest.main()
