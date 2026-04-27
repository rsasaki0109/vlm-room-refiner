"""CLI: 部屋画像を1枚与え、JSON分析結果を標準出力に出す。"""

from __future__ import annotations

import argparse
import json
import os
import sys

from vlm import analyze_room


def main() -> None:
    p = argparse.ArgumentParser(description="部屋画像のインテリア分析 (Ollama + Qwen2.5-VL)")
    p.add_argument("image", help="画像ファイルのパス")
    p.add_argument(
        "--style", default=os.environ.get("VR_STYLE"), help="目標の雰囲気 (任意)"
    )
    p.add_argument("--budget", default=os.environ.get("VR_BUDGET"), help="予算感 (任意)")
    p.add_argument(
        "--before-after", action="store_true", help="Before/After 的な文を加える"
    )
    args = p.parse_args()
    if not os.path.isfile(args.image):
        print("ファイルが存在しません:", args.image, file=sys.stderr)
        raise SystemExit(1)
    out = analyze_room(
        args.image,
        style_target=args.style,
        budget=args.budget,
        want_before_after=args.before_after,
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
