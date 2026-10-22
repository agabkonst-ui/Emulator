"""Тесты команды history и записи истории."""

import unittest

from support import make_session, run


class HistoryTest(unittest.TestCase):
    """Проверки history."""

    def setUp(self):
        """Создаёт сеанс с примером VFS."""
        self.session = make_session()

    def test_lists_commands_with_numbers(self):
        """Команды нумеруются с единицы, history видит и себя."""
        out, _err = run(self.session, "pwd", "ls d1", "history")
        self.assertEqual(
            out.splitlines()[2:],
            ["    1  pwd", "    2  ls d1", "    3  history"])

    def test_records_errors_but_not_blank_lines(self):
        """Ошибочные строки попадают в историю, пустые — нет."""
        run(self.session, "foo", "", "   ", 'ls "x')
        self.assertEqual(self.session.history, ["foo", 'ls "x'])

    def test_last_n(self):
        """history N выводит последние N записей с их номерами."""
        out, _err = run(self.session, "pwd", "pwd", "pwd", "history 2")
        self.assertEqual(
            out.splitlines()[3:], ["    3  pwd", "    4  history 2"])

    def test_zero_prints_nothing(self):
        """history 0 ничего не выводит."""
        out, _err = run(self.session, "pwd", "history 0")
        self.assertEqual(out, "/\n")

    def test_clear(self):
        """history -c очищает историю, нумерация начинается заново."""
        out, _err = run(self.session, "pwd", "history -c", "history")
        self.assertEqual(out, "/\n    1  history\n")

    def test_errors(self):
        """Нечисловой аргумент, опция и лишние аргументы — ошибки."""
        _out, err = run(self.session, "history x", "history -5",
                        "history 1 2")
        self.assertIn("требуется числовой аргумент", err)
        self.assertIn("неверная опция", err)
        self.assertIn("слишком много аргументов", err)


if __name__ == "__main__":
    unittest.main()
