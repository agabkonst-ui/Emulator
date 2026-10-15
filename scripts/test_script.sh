#!/bin/sh
# Проверка параметра --script: стартовый скрипт выполняется с эхом.
cd "$(dirname "$0")/.." || exit 1
sh ./run.sh --script examples/startup.txt
