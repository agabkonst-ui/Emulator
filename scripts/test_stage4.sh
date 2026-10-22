#!/bin/sh
# Этап 4: стартовый скрипт ls, cd, pwd, history, tail (с VFS и без неё).
cd "$(dirname "$0")/.." || exit 1
echo "=== stage4.json ==="
sh ./run.sh --vfs examples/vfs/stage4.json --script examples/stage4.txt
echo "код возврата: $?"
echo "=== deep.json ==="
sh ./run.sh --vfs examples/vfs/deep.json --script examples/stage4.txt
echo "код возврата: $?"
echo "=== без VFS ==="
sh ./run.sh --script examples/stage4.txt
echo "код возврата: $?"
