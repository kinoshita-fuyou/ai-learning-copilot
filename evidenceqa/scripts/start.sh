#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate
# 默认离线模板回答；配置 OPENAI_API_KEY 且想用真实 LLM 时去掉下一行
export EVIDENCEQA_ANSWER_PROVIDER="${EVIDENCEQA_ANSWER_PROVIDER:-template}"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
