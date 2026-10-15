#!/bin/sh
# Проверка параметра --vfs: путь выводится в отладочном выводе.
cd "$(dirname "$0")/.." || exit 1
sh ./run.sh --vfs examples/vfs/several.json < /dev/null
