#!/bin/sh
# Проверка обоих параметров (--vfs и --script) одновременно.
cd "$(dirname "$0")/.." || exit 1
sh ./run.sh --vfs examples/vfs.json --script examples/startup.txt
