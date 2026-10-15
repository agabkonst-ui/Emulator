#!/bin/sh
cd "$(dirname "$0")" || exit 1
for py in python3 python; do
    if "$py" -c "import sys" >/dev/null 2>&1; then
        PYTHONUTF8=1 PYTHONPATH=src exec "$py" -m shell_emulator "$@"
    fi
done
echo "Python not found. Install Python 3.8+ and retry." >&2
exit 1
