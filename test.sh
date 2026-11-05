#!/bin/sh
set -eu
cd "$(dirname "$0")"
export PYTHONPATH=src
export PYTHONDONTWRITEBYTECODE=1
exec "${PYTHON_EXE:-python3}" -B -m unittest discover -s tests -v
