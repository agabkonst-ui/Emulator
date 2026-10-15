#!/bin/sh
# Стартовый скрипт всех команд: с VFS, с другой VFS и без VFS.
cd "$(dirname "$0")/.." || exit 1
echo "=== deep.json ==="
sh ./run.sh --vfs examples/vfs/deep.json --script examples/full_demo.txt
echo "=== several.json ==="
sh ./run.sh --vfs examples/vfs/several.json --script examples/full_demo.txt
echo "=== без VFS ==="
sh ./run.sh --script examples/full_demo.txt
