#!/usr/bin/env bash
# Ollama が応答し、VLM 用タグ名の目安を表示する。
set -euo pipefail
HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
u="${HOST%/}/api/tags"
echo "GET $u"
if ! code=$(curl -sS -o /tmp/ollama-tags.json -w "%{http_code}" "$u"); then
  echo "FAIL: curl できません（Ollama は起動していますか？）" >&2
  exit 1
fi
echo "HTTP $code"
if [[ "$code" != "200" ]]; then
  echo "FAIL: 期待 200" >&2
  exit 1
fi
echo "OK. 候補モデル（qwen|vl|vision を含む行）:"
if command -v jq &>/dev/null; then
  jq -r '.models[].name' /tmp/ollama-tags.json 2>/dev/null | grep -Ei 'qwen|vl|vision' || true
  echo "--- 全名 ---"
  jq -r '.models[].name' /tmp/ollama-tags.json
else
  head -c 2000 /tmp/ollama-tags.json
  echo
fi
rm -f /tmp/ollama-tags.json
