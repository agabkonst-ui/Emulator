"""Точка запуска эмулятора: параметры, VFS, скрипт и интерактивный режим."""

import sys

from .commands import ShellExit
from .config import DEBUG_PREFIX, format_debug, parse_args
from .repl import build_prompt, repl
from .script import load_script, run_script
from .vfs import VfsError, format_summary, load_vfs

SCRIPT_ERROR_CODE = 2
VFS_ERROR_CODE = 3


class StartupError(Exception):
    """Ошибка запуска эмулятора с сообщением и кодом возврата."""

    def __init__(self, message, code):
        """Сохраняет сообщение об ошибке и код возврата."""
        super().__init__(message)
        self.code = code


def load_vfs_option(path, out):
    """Загружает VFS по параметру --vfs; без параметра возвращает None."""
    if path is None:
        return None
    try:
        vfs = load_vfs(path)
    except VfsError as error:
        raise StartupError(
            f"не удалось загрузить VFS: {error}", VFS_ERROR_CODE) from None
    print(f"{DEBUG_PREFIX} VFS загружена: {format_summary(vfs)}", file=out)
    return vfs


def load_script_option(path):
    """Читает скрипт по параметру --script; без параметра — пустой список."""
    if path is None:
        return []
    try:
        return load_script(path)
    except (OSError, UnicodeDecodeError) as error:
        raise StartupError(
            f"не удалось прочитать скрипт {path}: {error}",
            SCRIPT_ERROR_CODE) from None


def main(argv=None, read=input, out=sys.stdout, err=sys.stderr):
    """Запускает эмулятор и возвращает код возврата.

    Сначала выводятся все заданные параметры, затем загружается VFS,
    выполняется стартовый скрипт (если указан) и начинается
    интерактивный режим.
    """
    args = parse_args(argv)
    for line in format_debug(args):
        print(line, file=out)
    out.flush()
    try:
        vfs = load_vfs_option(args.vfs, out)
        lines = load_script_option(args.script)
    except StartupError as error:
        print(f"ошибка: {error}", file=err)
        return error.code
    prompt = build_prompt()
    try:
        run_script(lines, prompt, out, err, vfs)
    except ShellExit as stop:
        return stop.code
    return repl(read, out, err, prompt, vfs)
