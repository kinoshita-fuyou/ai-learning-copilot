#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo "未找到 .venv，请先执行："
  echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

source .venv/bin/activate

export EVIDENCEQA_DB_PATH="$PWD/demo.db"
python scripts/seed_demo.py --db "$EVIDENCEQA_DB_PATH"

echo "启动服务：http://127.0.0.1:8001"
uvicorn app.main:app --host 127.0.0.1 --port 8001 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

sleep 1
if command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:8001" || true
fi

wait "$SERVER_PID"
