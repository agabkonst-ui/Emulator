#!/bin/sh
# Варианты VFS (минимальный, несколько файлов, 3+ уровня) через stdin.
cd "$(dirname "$0")/.." || exit 1
echo "=== VFS: minimal ==="
sh ./run.sh --vfs examples/vfs/minimal.json < examples/vfs_check.txt
echo "=== VFS: several ==="
sh ./run.sh --vfs examples/vfs/several.json < examples/vfs_check.txt
echo "=== VFS: deep ==="
sh ./run.sh --vfs examples/vfs/deep.json < examples/vfs_check.txt
