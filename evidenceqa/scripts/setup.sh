#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo "创建虚拟环境 .venv ..."
  env -u PYTHONPATH python3 -m venv .venv
fi

echo "安装依赖（隔离 PYTHONPATH，避免误用系统/其他环境的包）..."
env -u PYTHONPATH .venv/bin/pip install -q -r requirements.txt

echo "完成。启动服务：./scripts/start.sh"
