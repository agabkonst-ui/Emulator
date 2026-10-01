"""Разбор строки ввода на команду и аргументы с поддержкой кавычек."""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
DOUBLE_QUOTE_ESCAPABLE = (DOUBLE_QUOTE, BACKSLASH)


class ParseError(Exception):
    """Ошибка разбора введённой строки."""


def _read_single_quoted(line, pos):
    """Читает текст в одинарных кавычках без экранирования.

    Возвращает прочитанный текст и позицию после закрывающей кавычки.
    """
    end = line.find(SINGLE_QUOTE, pos)
    if end == -1:
        raise ParseError("незакрытая одинарная кавычка")
    return line[pos:end], end + 1


def _read_double_quoted(line, pos):
    """Читает текст в двойных кавычках с поддержкой \\" и \\.

    Возвращает прочитанный текст и позицию после закрывающей кавычки.
    """
    chars = []
    while pos < len(line):
        char = line[pos]
        if char == DOUBLE_QUOTE:
            return "".join(chars), pos + 1
        next_pos = pos + 1
        if (char == BACKSLASH and next_pos < len(line)
                and line[next_pos] in DOUBLE_QUOTE_ESCAPABLE):
            char = line[next_pos]
            pos = next_pos
        chars.append(char)
        pos += 1
    raise ParseError("незакрытая двойная кавычка")


def _read_escaped(line, pos):
    """Читает символ после обратной косой черты вне кавычек."""
    if pos >= len(line):
        raise ParseError("обратная косая черта в конце строки")
    return line[pos], pos + 1


def tokenize(line):
    """Разбивает строку на слова, учитывая кавычки и экранирование.

    Пустые кавычки ('' или "") дают пустой аргумент.
    """
    tokens = []
    current = []
    in_token = False
    pos = 0
    while pos < len(line):
        char = line[pos]
        pos += 1
        if char.isspace():
            if in_token:
                tokens.append("".join(current))
                current, in_token = [], False
            continue
        in_token = True
        if char == SINGLE_QUOTE:
            text, pos = _read_single_quoted(line, pos)
        elif char == DOUBLE_QUOTE:
            text, pos = _read_double_quoted(line, pos)
        elif char == BACKSLASH:
            text, pos = _read_escaped(line, pos)
        else:
            text = char
        current.append(text)
    if in_token:
        tokens.append("".join(current))
    return tokens


def parse_line(line):
    """Возвращает пару (команда, список аргументов).

    Для пустой строки команда равна None.
    """
    tokens = tokenize(line)
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]
