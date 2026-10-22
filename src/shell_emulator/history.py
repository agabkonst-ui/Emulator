"""Команда history: просмотр и очистка истории введённых команд."""

from .errors import CommandError
from .options import is_option

CLEAR_ARG = "-c"
MAX_ARGS = 1
FIRST_INDEX = 1
INDEX_WIDTH = 5


def parse_count(text):
    """Разбирает необязательное число последних записей."""
    if is_option(text):
        raise CommandError(f"history: {text}: неверная опция")
    if not text.isdecimal():
        raise CommandError(f"history: {text}: требуется числовой аргумент")
    return int(text)


def format_history(items, first):
    """Нумерует записи истории начиная с номера first."""
    return "\n".join(f"{number:>{INDEX_WIDTH}}  {line}"
                     for number, line in enumerate(items, first))


def cmd_history(args, session):
    """history [N | -c]: вывод последних N записей или очистка истории."""
    if len(args) > MAX_ARGS:
        raise CommandError("history: слишком много аргументов")
    if args == [CLEAR_ARG]:
        session.history.clear()
        return None
    items = session.history
    if args:
        count = parse_count(args[0])
        items = items[-count:] if count else []
    first = len(session.history) - len(items) + FIRST_INDEX
    return format_history(items, first)
