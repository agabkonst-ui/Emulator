#!/bin/sh
# Варианты VFS (минимальный, несколько файлов, 3+ уровня) через --script.
cd "$(dirname "$0")/.." || exit 1
echo "=== VFS: minimal ==="
sh ./run.sh --vfs examples/vfs/minimal.json --script examples/vfs_check.txt
echo "=== VFS: several ==="
sh ./run.sh --vfs examples/vfs/several.json --script examples/vfs_check.txt
echo "=== VFS: deep ==="
sh ./run.sh --vfs examples/vfs/deep.json --script examples/vfs_check.txt
