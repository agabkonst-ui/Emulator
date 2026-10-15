#!/bin/sh
# Ошибки загрузки VFS: файл не найден, неверный формат, не файл.
cd "$(dirname "$0")/.." || exit 1
echo "=== VFS: missing.json ==="
sh ./run.sh --vfs examples/vfs/missing.json < /dev/null
echo "код возврата: $?"
echo "=== VFS: bad_json.json ==="
sh ./run.sh --vfs examples/vfs/bad_json.json < /dev/null
echo "код возврата: $?"
echo "=== VFS: bad_type.json ==="
sh ./run.sh --vfs examples/vfs/bad_type.json < /dev/null
echo "код возврата: $?"
echo "=== VFS: bad_base64.json ==="
sh ./run.sh --vfs examples/vfs/bad_base64.json < /dev/null
echo "код возврата: $?"
echo "=== VFS: bad_root.json ==="
sh ./run.sh --vfs examples/vfs/bad_root.json < /dev/null
echo "код возврата: $?"
echo "=== VFS: каталог вместо файла ==="
sh ./run.sh --vfs examples < /dev/null
echo "код возврата: $?"
