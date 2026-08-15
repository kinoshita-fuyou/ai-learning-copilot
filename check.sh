#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

for project in evidenceqa reportflow; do
  if [ ! -x "$project/.venv/bin/python" ]; then
    echo "== ${project}：未找到 .venv，请先执行 ./${project}/scripts/setup.sh"
    exit 1
  fi
  echo "== ${project}：运行测试"
  (cd "$project" && env -u PYTHONPATH .venv/bin/python -m pytest -q)
done

echo "== 全部通过 =="
