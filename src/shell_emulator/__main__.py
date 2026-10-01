"""Точка входа: python -m shell_emulator."""

import sys

from .repl import repl

if __name__ == "__main__":
    sys.exit(repl())
