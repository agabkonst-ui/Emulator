"""Точка запуска эмулятора: параметры, скрипт и интерактивный режим."""

import sys

from .commands import ShellExit
from .config import format_debug, parse_args
from .repl import build_prompt, repl
from .script import load_script, run_script

SCRIPT_ERROR_CODE = 2


def main(argv=None, read=input, out=sys.stdout, err=sys.stderr):
    """Запускает эмулятор и возвращает код возврата.

    Сначала выводятся все заданные параметры, затем выполняется стартовый
    скрипт (если указан), после чего начинается интерактивный режим.
    """
    args = parse_args(argv)
    for line in format_debug(args):
        print(line, file=out)
    out.flush()
    prompt = build_prompt()
    if args.script is not None:
        try:
            lines = load_script(args.script)
        except (OSError, UnicodeDecodeError) as error:
            print(f"ошибка: не удалось прочитать скрипт "
                  f"{args.script}: {error}", file=err)
            return SCRIPT_ERROR_CODE
        try:
            run_script(lines, prompt, out, err)
        except ShellExit as stop:
            return stop.code
    return repl(read, out, err, prompt)
