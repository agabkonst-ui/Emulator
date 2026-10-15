#!/bin/sh
# Ошибки: отсутствующий скрипт, неизвестный и неполный параметр.
cd "$(dirname "$0")/.." || exit 1
sh ./run.sh --script examples/missing.txt
echo "код возврата: $?"
sh ./run.sh --unknown
echo "код возврата: $?"
sh ./run.sh --vfs
echo "код возврата: $?"
