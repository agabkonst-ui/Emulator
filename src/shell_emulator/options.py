"""Разбор коротких опций команд: -a, -l, объединённые -la и '--'."""

from .errors import CommandError

OPTION_PREFIX = "-"
END_OF_OPTIONS = "--"


def is_option(arg):
    """Проверяет, что аргумент — опция, а не операнд или одиночный '-'."""
    return arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX


def check_letters(name, arg, allowed):
    """Возвращает буквы опций аргумента, проверяя их по списку allowed."""
    letters = arg[len(OPTION_PREFIX):]
    for letter in letters:
        if letter not in allowed:
            raise CommandError(f"{name}: неверная опция -- '{letter}'")
    return letters


def parse_flags(name, args, allowed):
    """Отделяет флаги от операндов.

    Опции могут стоять между операндами; после '--' все аргументы
    считаются операндами. Возвращает пару (множество флагов, операнды).
    """
    flags, operands = set(), []
    options_done = False
    for arg in args:
        if options_done or not is_option(arg):
            operands.append(arg)
        elif arg == END_OF_OPTIONS:
            options_done = True
        else:
            flags.update(check_letters(name, arg, allowed))
    return flags, operands
