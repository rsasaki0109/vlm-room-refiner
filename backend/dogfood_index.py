"""Dogfooding index generator: notes/dogfooding/*.md を集計して index.md を作る。"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Row:
    file: str
    persona_key: str
    image: str
    model: str
    ran_at: str
    has_error: bool
    conclusion: str
    flags: str


def _first_line_after(md: str, heading: str) -> str:
    # heading like "## 結論"
    i = md.find(heading)
    if i < 0:
        return ""
    tail = md[i + len(heading) :]
    lines = [l.rstrip() for l in tail.splitlines()]
    for l in lines:
        if l.strip().startswith("- "):
            return l.strip()[2:].strip()
    return ""


def _field(md: str, name: str) -> str:
    # list item: "- name: `...`" or "- name: ..."
    m = re.search(rf"^- {re.escape(name)}:\s*(.*)$", md, flags=re.MULTILINE)
    if not m:
        return ""
    v = m.group(1).strip()
    if v.startswith("`") and v.endswith("`"):
        return v[1:-1]
    return v


def _has_error(md: str) -> bool:
    return "_error" in md or "失敗" in md


def _flags(md: str) -> str:
    # 非現実/工事っぽいキーワードをざっくり検出（dogfoodingで早期に拾う用）
    bad = []
    patterns = [
        (r"壁紙|塗装|張り替え|床材|フローリング", "reform"),
        (r"天井|ダウンライト|配線工事|電気工事|増設|設置", "work"),
        (r"窓を設置|壁を壊す", "forbidden"),
    ]
    for pat, tag in patterns:
        if re.search(pat, md):
            bad.append(tag)
    return ",".join(sorted(set(bad)))


def main() -> None:
    p = argparse.ArgumentParser(description="Generate dogfooding index.md")
    p.add_argument("--dir", default="notes/dogfooding", help="notes dir (repo root relative)")
    args = p.parse_args()

    repo = Path(__file__).resolve().parents[1]
    d = (repo / args.dir).resolve()
    files = sorted([p for p in d.glob("*.md") if p.name != "README.md" and p.name != "index.md"])

    rows: list[Row] = []
    for f in files:
        md = f.read_text(encoding="utf-8", errors="replace")
        header = md.splitlines()[0] if md.splitlines() else ""
        # "# Dogfooding: persona × image"
        persona_key = ""
        image = ""
        m = re.match(r"^# Dogfooding:\s*([^ ]+)\s*×\s*(.+)$", header)
        if m:
            persona_key = m.group(1).strip()
            image = m.group(2).strip()
        rows.append(
            Row(
                file=f.name,
                persona_key=persona_key or _field(md, "ペルソナ").split("/")[0].strip("` ").strip(),
                image=_field(md, "画像") or image,
                model=_field(md, "モデル"),
                ran_at=_field(md, "実行日時"),
                has_error=_has_error(md),
                conclusion=_first_line_after(md, "## 結論") or "",
                flags=_flags(md),
            )
        )

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    ok = sum(1 for r in rows if not r.has_error)
    ng = sum(1 for r in rows if r.has_error)

    lines: list[str] = []
    lines += ["# dogfooding index", ""]
    lines += [f"- generated: `{now}`", f"- reports: `{len(rows)}` (ok={ok}, error={ng})", ""]
    lines += [
        "## 一覧",
        "",
        "| report | persona | image | model | time | status | flags | 結論 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        status = "error" if r.has_error else "ok"
        concl = (r.conclusion or "").replace("|", "\\|")
        lines.append(
            f"| `{r.file}` | `{r.persona_key}` | `{Path(r.image).name}` | `{r.model}` | `{r.ran_at}` | **{status}** | `{r.flags}` | {concl} |"
        )

    lines += ["", "## 次アクション", "", "- `ok` のレポートから、誤字/抽象表現/非現実提案のパターンを拾って `backend/prompt.py` を1点ずつ改善。", ""]

    (d / "index.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

