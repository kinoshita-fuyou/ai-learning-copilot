#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate
# 默认离线规则代理；配置好 OPENAI_API_KEY 后 export REPORTFLOW_AGENT=llm 可启用真实工具调用
export REPORTFLOW_AGENT="${REPORTFLOW_AGENT:-rule}"
env -u PYTHONPATH uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
