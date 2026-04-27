#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt

: "${OLLAMA_HOST:=http://127.0.0.1:11434}"
: "${OLLAMA_MODEL:=qwen3-vl:4b}"
: "${OLLAMA_TIMEOUT_SECONDS:=600}"

echo "OLLAMA_HOST=$OLLAMA_HOST"
echo "OLLAMA_MODEL=$OLLAMA_MODEL"
echo "OLLAMA_TIMEOUT_SECONDS=$OLLAMA_TIMEOUT_SECONDS"

python dogfood.py --images dogfood-input --personas dogfooding/personas.json --out notes/dogfooding
python dogfood_index.py --dir notes/dogfooding

echo "Wrote: $ROOT/notes/dogfooding/index.md"

