"""Команда tail: последние строки или байты файлов VFS."""

from dataclasses import dataclass

from .errors import CommandError
from .options import END_OF_OPTIONS, OPTION_PREFIX, is_option
from .vfs import VfsDir

DEFAULT_LINES = 10
LINES_OPTION = "n"
BYTES_OPTION = "c"
QUIET_OPTION = "q"
VERBOSE_OPTION = "v"
FROM_START_MARK = "+"
START_OFFSET = 1
SINGLE_FILE = 1
NEWLINE = "\n"
HEADER_FORMAT = "==> {} <=="
BLOCK_SEPARATOR = "\n\n"
UNIT_NAMES = {LINES_OPTION: "строк", BYTES_OPTION: "байт"}


@dataclass
class TailOptions:
    """Параметры tail: единица счёта, число, отсчёт с начала, заголовки.

    Поле headers: None — по числу файлов, True — всегда, False — никогда.
    """

    unit: str = LINES_OPTION
    count: int = DEFAULT_LINES
    from_start: bool = False
    headers: object = None


def parse_count(unit, text):
    """Разбирает значение -n или -c: N (с конца) или +N (с позиции N)."""
    from_start = text.startswith(FROM_START_MARK)
    digits = text[len(FROM_START_MARK):] if from_start else text
    if not digits.isdecimal():
        raise CommandError(
            f"tail: {text}: неверное число {UNIT_NAMES[unit]}")
    return int(digits), from_start


def set_count(options, unit, text):
    """Сохраняет в параметрах единицу счёта и число из значения опции."""
    options.unit = unit
    options.count, options.from_start = parse_count(unit, text)


def take_value(letter, pending):
    """Берёт значение опции из следующего аргумента."""
    if not pending:
        raise CommandError(f"tail: опция требует аргумент -- '{letter}'")
    return pending.pop(0)


def apply_option(options, arg, pending):
    """Применяет одну опцию tail; значение может быть в pending."""
    body = arg[len(OPTION_PREFIX):]
    letter, value = body[:1], body[1:]
    if body.isdecimal():
        set_count(options, LINES_OPTION, body)
    elif letter in (LINES_OPTION, BYTES_OPTION):
        set_count(options, letter, value or take_value(letter, pending))
    elif body in (QUIET_OPTION, VERBOSE_OPTION):
        options.headers = body == VERBOSE_OPTION
    else:
        raise CommandError(f"tail: неверная опция -- '{letter}'")


def parse_tail_args(args):
    """Разбирает аргументы tail и возвращает (параметры, список файлов)."""
    options, files = TailOptions(), []
    pending = list(args)
    options_done = False
    while pending:
        arg = pending.pop(0)
        if options_done or not is_option(arg):
            files.append(arg)
        elif arg == END_OF_OPTIONS:
            options_done = True
        else:
            apply_option(options, arg, pending)
    return options, files


def cut(items, options):
    """Выбирает последние (или начиная с позиции N) элементы."""
    if options.from_start:
        return items[max(options.count - START_OFFSET, 0):]
    return items[-options.count:] if options.count else items[:0]


def strip_newline(text):
    """Убирает один завершающий перевод строки (его добавит print)."""
    return text[:-len(NEWLINE)] if text.endswith(NEWLINE) else text


def tail_text(data, options):
    """Возвращает нужную часть содержимого файла в виде текста."""
    if options.unit == BYTES_OPTION:
        text = cut(data, options).decode("utf-8", errors="replace")
        return strip_newline(text)
    lines = data.decode("utf-8", errors="replace").split(NEWLINE)
    if lines[-1] == "":
        lines.pop()
    return NEWLINE.join(cut(lines, options))


def read_file(session, path):
    """Возвращает байты файла VFS или сообщает об ошибке."""
    node = session.find(path)
    if node is None:
        raise CommandError(
            f"tail: невозможно открыть '{path}' для чтения: "
            "нет такого файла или каталога")
    if isinstance(node, VfsDir):
        raise CommandError(f"tail: {path}: это каталог")
    return node.data


def cmd_tail(args, session):
    """tail [-n N | -N] [-c N] [-q | -v] файл...: конец файлов VFS.

    N — число последних строк (по умолчанию 10) или байтов; +N означает
    «начиная с N-й». Заголовки '==> имя <==' печатаются при нескольких
    файлах (-q скрывает их, -v показывает всегда).
    """
    options, files = parse_tail_args(args)
    if not files:
        raise CommandError("tail: не указан файл "
                           "(чтение со стандартного ввода не поддерживается)")
    headers = options.headers
    if headers is None:
        headers = len(files) > SINGLE_FILE
    blocks, errors = [], []
    for path in files:
        try:
            body = tail_text(read_file(session, path), options)
        except CommandError as error:
            errors.append(str(error))
            continue
        blocks.append(f"{HEADER_FORMAT.format(path)}\n{body}"
                      if headers else body)
    output = (BLOCK_SEPARATOR if headers else NEWLINE).join(blocks)
    if errors:
        raise CommandError(NEWLINE.join(errors), output or None)
    return output
