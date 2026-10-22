"""Стартовый скрипт: чтение и выполнение команд эмулятора."""

from .repl import build_prompt, run_line

COMMENT_MARK = "#"


def load_script(path):
    """Читает стартовый скрипт и возвращает список его строк."""
    with open(path, encoding="utf-8-sig") as handle:
        return handle.read().splitlines()


def is_skipped(line):
    """Проверяет, что строка пустая или является комментарием."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_MARK)


def run_script(lines, out, err, session, prompt_for=build_prompt):
    """Выполняет строки скрипта, имитируя диалог с пользователем.

    Для каждой строки выводится приглашение (с текущим каталогом) и
    введённая команда, затем её результат. Ошибочные строки сообщают
    об ошибке и пропускаются.
    Команда exit завершает скрипт исключением ShellExit.
    """
    for line in lines:
        if is_skipped(line):
            continue
        print(f"{prompt_for(session.cwd)}{line}", file=out)
        out.flush()
        run_line(line, out, err, session)
        out.flush()
