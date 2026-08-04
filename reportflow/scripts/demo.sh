#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo "未找到 .venv，请先执行："
  echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

source .venv/bin/activate
export REPORTFLOW_AGENT="${REPORTFLOW_AGENT:-rule}"

echo "启动服务：http://127.0.0.1:8002"
uvicorn app.main:app --host 127.0.0.1 --port 8002 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

echo "等待服务就绪..."
for _ in $(seq 1 20); do
  if curl -sf http://127.0.0.1:8002/health >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
echo ""
echo "===== 示例：生成本周销售周报 ====="
curl -s -X POST http://127.0.0.1:8002/report \
  -H "Content-Type: application/json" \
  -d '{"task":"生成本周销售周报"}' | python3 -m json.tool | head -70
echo ""
echo "===== 示例：故意让 query_sales 失败，观察降级 ====="
curl -s -X POST http://127.0.0.1:8002/report \
  -H "Content-Type: application/json" \
  -d '{"task":"生成本周销售周报","simulate_failure":["query_sales"]}' \
  | python3 -m json.tool | head -50

if command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:8002/docs" || true
fi

wait "$SERVER_PID"
