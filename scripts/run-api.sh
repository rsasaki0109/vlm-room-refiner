#!/usr/bin/env bash
# API 用 uvicorn。venv を作り requirements を入れてから起動する。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
PORT="${API_PORT:-8010}"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
