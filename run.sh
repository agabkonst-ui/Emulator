#!/bin/sh
cd "$(dirname "$0")" || exit 1
export PYTHONDONTWRITEBYTECODE=1
if [ -n "${PYTHON_EXE:-}" ]; then
    PYTHONUTF8=1 PYTHONPATH=src exec "$PYTHON_EXE" -B -m shell_emulator "$@"
fi
for py in python3 python; do
    if "$py" -c "import sys" >/dev/null 2>&1; then
        PYTHONUTF8=1 PYTHONPATH=src exec "$py" -m shell_emulator "$@"
    fi
done
echo "Python not found. Install Python 3.8+ and retry." >&2
exit 1
