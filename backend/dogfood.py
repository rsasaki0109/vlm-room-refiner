"""Dogfooding harness: 複数ペルソナ×複数画像で /analyze 相当をバッチ実行し、notes に記録する。

- 入力画像はコミットしない（dogfood-input/ を想定）
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from vlm import analyze_room


@dataclass(frozen=True)
class Persona:
    key: str
    name: str
    style: str | None = None
    budget: str | None = None
    before_after: bool = True
    note: str | None = None


def _load_personas(path: Path) -> list[Persona]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: list[Persona] = []
    for p in obj.get("personas", []):
        out.append(
            Persona(
                key=str(p["key"]),
                name=str(p["name"]),
                style=p.get("style"),
                budget=p.get("budget"),
                before_after=bool(p.get("before_after", True)),
                note=p.get("note"),
            )
        )
    if not out:
        raise ValueError("no personas found")
    return out


def _iter_images(dir_path: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp", ".svg"}
    imgs = [p for p in sorted(dir_path.iterdir()) if p.suffix.lower() in exts and p.is_file()]
    if not imgs:
        raise ValueError(f"no images under {dir_path}")
    return imgs


def _md_escape(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def _render_report(
    *,
    abs_repo_root: Path,
    image_path: Path,
    persona: Persona,
    result: dict[str, Any],
    model_name: str,
) -> str:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    # Keep JSON snippet small but readable
    snippet = json.dumps(result, ensure_ascii=False, indent=2)
    if len(snippet) > 6000:
        snippet = snippet[:6000] + "\n…(truncated)…\n"

    facts = [
        f"- 実行日時: `{now}`",
        f"- 画像: `{image_path}`",
        f"- モデル: `{model_name}`",
        f"- ペルソナ: `{persona.key}` / {persona.name}",
    ]
    if persona.style:
        facts.append(f"- style: `{persona.style}`")
    if persona.budget:
        facts.append(f"- budget: `{persona.budget}`")
    facts.append(f"- before_after: `{persona.before_after}`")
    if persona.note:
        facts.append(f"- メモ: {_md_escape(persona.note)}")

    # inference hints: separate facts from inference
    infer = []
    if "_error" in result:
        infer.append(f"- **失敗**: `_error` = `{result.get('_error')}`")
    else:
        infer.append("- 出力は JSON スキーマ形状（room_type/style/problems/recommendations/shopping_keywords）に収まっている。")
        infer.append("- 表現が抽象的/誤字がある場合は `backend/prompt.py` を強化する。")

    return "\n".join(
        [
            f"# Dogfooding: {persona.key} × {image_path.name}",
            "",
            "## 結論",
            "",
            "- (要約を一行で追記してください。例: “韓国風を指定すると照明/色温度が提案に入った”)",
            "",
            "## 確認済み事実",
            "",
            *facts,
            "",
            "### モデル出力（JSON）",
            "",
            "```json",
            snippet,
            "```",
            "",
            "## 未確認/要確認項目",
            "",
            *infer,
            "",
            "## 次アクション",
            "",
            "- 推奨: problems/recommendations の“具体性”を点検し、プロンプトを微修正 → 同画像で再実行して差分比較。",
            "",
            "## 絶対パス",
            "",
            f"- repo: `{abs_repo_root}`",
            "",
        ]
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Dogfooding: personas x images -> notes markdown")
    p.add_argument("--personas", default="dogfooding/personas.json", help="ペルソナJSONへの相対パス（repo root 起点）")
    p.add_argument("--images", default="dogfood-input", help="画像ディレクトリ（repo root 起点。コミットしない）")
    p.add_argument("--out", default="notes/dogfooding", help="出力先ディレクトリ（repo root 起点）")
    args = p.parse_args()

    repo = Path(__file__).resolve().parents[1]
    personas_path = (repo / args.personas).resolve()
    images_dir = (repo / args.images).resolve()
    out_dir = (repo / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    personas = _load_personas(personas_path)
    images = _iter_images(images_dir)

    model_name = os.environ.get("OLLAMA_MODEL") or "qwen3-vl:8b (default/fallback)"

    wrote = 0
    failed = 0
    for img in images:
        for persona in personas:
            try:
                r = analyze_room(
                    str(img),
                    style_target=persona.style,
                    budget=persona.budget,
                    want_before_after=persona.before_after,
                )
            except Exception as e:
                failed += 1
                r = {
                    "_error": f"analyze_room: {type(e).__name__}: {e}",
                    "room_type": "判別困難（エラー）",
                    "style": "判別困難（エラー）",
                    "problems": ["(エラーのため未取得)"],
                    "recommendations": ["(エラーのため未取得)"],
                    "shopping_keywords": ["(エラーのため未取得)"],
                }
            img_key = img.name.replace(" ", "_").replace(".", "_")
            slug = f"{img_key}__{persona.key}"
            dest = out_dir / f"{slug}.md"
            dest.write_text(
                _render_report(
                    abs_repo_root=repo,
                    image_path=img,
                    persona=persona,
                    result=r,
                    model_name=model_name,
                ),
                encoding="utf-8",
            )
            wrote += 1

    print(f"wrote {wrote} reports to {out_dir} (failed={failed})", file=sys.stderr)


if __name__ == "__main__":
    main()

