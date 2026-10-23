"""Общие помощники тестов: VFS из словаря и запуск строк команд."""

import io

from shell_emulator.repl import run_line
from shell_emulator.session import new_session
from shell_emulator.vfs import Vfs, parse_node

SAMPLE_VFS = {
    "type": "dir",
    "children": {
        "a.txt": {"type": "file", "content": "один\nдва\nтри\n"},
        ".hidden": {"type": "file", "content": "x"},
        "ascii.txt": {"type": "file", "content": "abc\ndef\n"},
        "bin.dat": {"type": "file", "encoding": "base64",
                    "content": "AAEC"},
        "no_eol.txt": {"type": "file", "content": "раз\nдва"},
        "d1": {"type": "dir", "children": {
            "d2": {"type": "dir", "children": {
                "deep.txt": {"type": "file", "content": "глубоко\n"}}}}},
        "empty": {"type": "dir"},
    },
}


def make_session(document=None):
    """Создаёт сеанс с VFS из словаря (по умолчанию SAMPLE_VFS)."""
    root = parse_node(document or SAMPLE_VFS, "/")
    return new_session(Vfs("test", root))


def run(session, *lines):
    """Выполняет строки в сеансе и возвращает (вывод, ошибки)."""
    out, err = io.StringIO(), io.StringIO()
    for line in lines:
        run_line(line, out, err, session)
    return out.getvalue(), err.getvalue()
