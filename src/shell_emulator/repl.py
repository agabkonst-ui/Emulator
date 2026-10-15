"""Интерактивный цикл (REPL) эмулятора."""

import getpass
import socket
import sys

from .commands import CommandError, ShellExit, execute
from .parser import ParseError, parse_line

HOME_MARK = "~"


def build_prompt():
    """Формирует приглашение вида username@hostname:~$ по данным ОС."""
    user = getpass.getuser()
    host = socket.gethostname()
    return f"{user}@{host}:{HOME_MARK}$ "


def run_line(line, out, err, vfs=None):
    """Выполняет одну строку ввода, печатая результат или ошибку."""
    try:
        name, args = parse_line(line)
        if name is None:
            return
        output = execute(name, args, vfs)
    except (ParseError, CommandError) as error:
        print(f"ошибка: {error}", file=err)
        return
    if output:
        print(output, file=out)


def repl(read=input, out=sys.stdout, err=sys.stderr, prompt=None,
         vfs=None):
    """Запускает цикл чтения команд и возвращает код возврата."""
    if prompt is None:
        prompt = build_prompt()
    while True:
        try:
            line = read(prompt)
        except EOFError:
            print("exit", file=out)
            return 0
        except KeyboardInterrupt:
            print(file=out)
            continue
        try:
            run_line(line, out, err, vfs)
        except ShellExit as stop:
            return stop.code
