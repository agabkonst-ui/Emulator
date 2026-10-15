"""Параметры командной строки эмулятора и их отладочный вывод."""

import argparse

PROG_NAME = "shell_emulator"
NOT_SET = "(не задан)"
DEBUG_PREFIX = "[отладка]"


def build_parser():
    """Создаёт разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="Эмулятор командной оболочки UNIX-подобной ОС.")
    parser.add_argument(
        "--vfs", metavar="ПУТЬ",
        help="путь к физическому расположению виртуальной файловой системы")
    parser.add_argument(
        "--script", metavar="ПУТЬ",
        help="путь к стартовому скрипту с командами эмулятора")
    return parser


def parse_args(argv=None):
    """Разбирает параметры; при ошибке завершает работу с кодом 2."""
    return build_parser().parse_args(argv)


def format_debug(args):
    """Возвращает строки отладочного вывода всех заданных параметров."""
    lines = [f"{DEBUG_PREFIX} Параметры запуска:"]
    for name, value in sorted(vars(args).items()):
        shown = NOT_SET if value is None else value
        lines.append(f"{DEBUG_PREFIX}   {name} = {shown}")
    return lines
