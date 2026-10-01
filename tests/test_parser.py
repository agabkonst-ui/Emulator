"""Тесты парсера строки ввода."""

import unittest

from shell_emulator.parser import ParseError, parse_line, tokenize


class TokenizeTest(unittest.TestCase):
    """Проверки разбиения строки на слова."""

    def test_plain_words(self):
        """Слова разделяются пробелами."""
        self.assertEqual(tokenize("ls  -l   /tmp"), ["ls", "-l", "/tmp"])

    def test_double_quotes(self):
        """Двойные кавычки сохраняют пробелы внутри аргумента."""
        self.assertEqual(tokenize('cd "My Docs"'), ["cd", "My Docs"])

    def test_single_quotes(self):
        """Одинарные кавычки не обрабатывают экранирование."""
        self.assertEqual(tokenize(r"ls 'a\b c'"), ["ls", r"a\b c"])

    def test_escaped_quote_in_double_quotes(self):
        """Внутри двойных кавычек можно экранировать кавычку."""
        self.assertEqual(tokenize(r'ls "a\"b"'), ["ls", 'a"b'])

    def test_empty_quotes_give_empty_argument(self):
        """Пустые кавычки дают пустой аргумент."""
        self.assertEqual(tokenize('ls ""'), ["ls", ""])

    def test_adjacent_quoted_parts_are_joined(self):
        """Соседние части слова склеиваются в один аргумент."""
        self.assertEqual(tokenize('ls a"b c"d'), ["ls", "ab cd"])

    def test_unclosed_quotes(self):
        """Незакрытые кавычки приводят к ошибке."""
        for line in ('ls "abc', "ls 'abc"):
            with self.assertRaises(ParseError):
                tokenize(line)

    def test_trailing_backslash(self):
        """Обратная косая черта в конце строки — ошибка."""
        with self.assertRaises(ParseError):
            tokenize("ls abc\\")


class ParseLineTest(unittest.TestCase):
    """Проверки выделения команды и аргументов."""

    def test_empty_line(self):
        """Пустая строка не содержит команды."""
        self.assertEqual(parse_line("   "), (None, []))

    def test_command_and_args(self):
        """Первое слово — команда, остальные — аргументы."""
        self.assertEqual(parse_line("cd 'a b'"), ("cd", ["a b"]))


if __name__ == "__main__":
    unittest.main()
