#!/usr/bin/env bash
# ROS 等のグローバル pytest プラグイン衝突を避ける
set -euo pipefail
cd "$(dirname "$0")"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements-dev.txt
exec python -m pytest tests/ "$@"
