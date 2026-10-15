"""Стартовый скрипт: чтение и выполнение команд эмулятора."""

from .repl import run_line

COMMENT_MARK = "#"


def load_script(path):
    """Читает стартовый скрипт и возвращает список его строк."""
    with open(path, encoding="utf-8-sig") as handle:
        return handle.read().splitlines()


def is_skipped(line):
    """Проверяет, что строка пустая или является комментарием."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_MARK)


def run_script(lines, prompt, out, err):
    """Выполняет строки скрипта, имитируя диалог с пользователем.

    Для каждой строки выводится приглашение с введённой командой, затем
    её результат. Ошибочные строки сообщают об ошибке и пропускаются.
    Команда exit завершает скрипт исключением ShellExit.
    """
    for line in lines:
        if is_skipped(line):
            continue
        print(f"{prompt}{line}", file=out)
        out.flush()
        run_line(line, out, err)
        out.flush()
