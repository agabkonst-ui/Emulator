#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
sh run.sh --vfs examples/vfs/stage5.json --script examples/stage5.txt
