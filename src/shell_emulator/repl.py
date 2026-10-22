"""Интерактивный цикл (REPL) эмулятора."""

import getpass
import socket
import sys

from .commands import CommandError, ShellExit, execute
from .parser import ParseError, parse_line
from .paths import ROOT_PATH
from .session import new_session


def build_prompt(cwd=ROOT_PATH):
    """Формирует приглашение вида username@hostname:/путь$ по данным ОС."""
    user = getpass.getuser()
    host = socket.gethostname()
    return f"{user}@{host}:{cwd}$ "


def record_history(line, session):
    """Добавляет непустую введённую строку в историю команд."""
    text = line.strip()
    if text:
        session.history.append(text)


def report_error(error, out, err):
    """Печатает вывод, полученный до ошибки, и сообщение об ошибке."""
    output = getattr(error, "output", None)
    if output:
        print(output, file=out)
    print(f"ошибка: {error}", file=err)


def run_line(line, out, err, session):
    """Выполняет одну строку ввода, печатая результат или ошибку."""
    record_history(line, session)
    try:
        name, args = parse_line(line)
        if name is None:
            return
        output = execute(name, args, session)
    except (ParseError, CommandError) as error:
        report_error(error, out, err)
        return
    if output:
        print(output, file=out)


def repl(read=input, out=sys.stdout, err=sys.stderr, session=None,
         prompt_for=build_prompt):
    """Запускает цикл чтения команд и возвращает код возврата."""
    if session is None:
        session = new_session()
    while True:
        try:
            line = read(prompt_for(session.cwd))
        except EOFError:
            print("exit", file=out)
            return 0
        except KeyboardInterrupt:
            print(file=out)
            continue
        try:
            run_line(line, out, err, session)
        except ShellExit as stop:
            return stop.code
