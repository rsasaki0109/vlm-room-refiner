#!/usr/bin/env python3
"""dogfood-input/ に合成の「部屋っぽい」PNGを置く（コミット対象外の検証用）。

Pillow が必要: pip install Pillow
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: tuple[int, int, int]) -> None:
    draw.rectangle(xy, fill=fill)


def synth_living_room(out: Path, w: int = 896, h: int = 672) -> None:
    img = Image.new("RGB", (w, h), (235, 232, 226))
    dr = ImageDraw.Draw(img)
    # floor / wall split (horizon ~ 58%)
    y_h = int(h * 0.58)
    _rect(dr, (0, y_h, w, h), (186, 170, 145))
    _rect(dr, (0, 0, w, y_h), (210, 212, 216))
    # window
    _rect(dr, (int(w * 0.72), int(h * 0.12), int(w * 0.92), int(h * 0.42)), (160, 190, 230))
    # sofa
    _rect(dr, (int(w * 0.12), int(h * 0.52), int(w * 0.52), int(h * 0.78)), (190, 120, 85))
    # coffee table
    _rect(dr, (int(w * 0.38), int(h * 0.62), int(w * 0.62), int(h * 0.74)), (120, 95, 70))
    # TV + stand
    _rect(dr, (int(w * 0.62), int(h * 0.42), int(w * 0.82), int(h * 0.52)), (40, 40, 42))
    _rect(dr, (int(w * 0.60), int(h * 0.52), int(w * 0.84), int(h * 0.62)), (90, 75, 60))
    # messy cables on floor (dark lines)
    for i in range(8):
        x0 = int(w * (0.25 + i * 0.06))
        dr.line((x0, int(h * 0.76), x0 + 30, int(h * 0.82)), fill=(55, 55, 55), width=3)
    img.save(out, format="PNG")


def synth_bedroom(out: Path, w: int = 896, h: int = 672) -> None:
    img = Image.new("RGB", (w, h), (230, 228, 235))
    dr = ImageDraw.Draw(img)
    y_h = int(h * 0.55)
    _rect(dr, (0, y_h, w, h), (175, 155, 135))
    _rect(dr, (0, 0, w, y_h), (195, 185, 205))
    # bed
    _rect(dr, (int(w * 0.08), int(h * 0.48), int(w * 0.72), int(h * 0.82)), (245, 245, 248))
    # pillows
    _rect(dr, (int(w * 0.14), int(h * 0.42), int(w * 0.34), int(h * 0.52)), (220, 220, 230))
    _rect(dr, (int(w * 0.34), int(h * 0.42), int(w * 0.54), int(h * 0.52)), (200, 200, 215))
    # nightstand clutter
    _rect(dr, (int(w * 0.74), int(h * 0.52), int(w * 0.92), int(h * 0.68)), (120, 90, 70))
    for i, c in enumerate([(230, 60, 60), (60, 120, 230), (230, 180, 40)]):
        _rect(dr, (int(w * 0.76 + i * 10), int(h * 0.46), int(w * 0.82 + i * 10), int(h * 0.52)), c)
    # floor lamp (circle top + pole)
    cx, cy = int(w * 0.88), int(h * 0.38)
    dr.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=(255, 230, 160))
    dr.rectangle((cx - 6, cy + 28, cx + 6, int(h * 0.82)), fill=(90, 90, 90))
    img.save(out, format="PNG")


def synth_desk_wfh(out: Path, w: int = 896, h: int = 672) -> None:
    img = Image.new("RGB", (w, h), (225, 225, 228))
    dr = ImageDraw.Draw(img)
    y_h = int(h * 0.52)
    _rect(dr, (0, y_h, w, h), (140, 125, 110))
    _rect(dr, (0, 0, w, y_h), (210, 215, 220))
    # desk
    _rect(dr, (int(w * 0.06), int(h * 0.48), int(w * 0.94), int(h * 0.62)), (160, 120, 85))
    # monitor
    _rect(dr, (int(w * 0.34), int(h * 0.22), int(w * 0.62), int(h * 0.42)), (30, 32, 35))
    _rect(dr, (int(w * 0.44), int(h * 0.42), int(w * 0.52), int(h * 0.50)), (50, 50, 52))
    # keyboard
    _rect(dr, (int(w * 0.36), int(h * 0.50), int(w * 0.60), int(h * 0.54)), (70, 70, 75))
    # cable spaghetti
    for a in range(16):
        t = a / 15.0
        x1 = int(w * 0.20 + 400 * t)
        y1 = int(h * 0.54 + 8 * math.sin(t * 6))
        x2 = x1 + 22
        y2 = y1 + 14
        dr.line((x1, y1, x2, y2), fill=(45, 45, 48), width=2)
    # bookshelf
    _rect(dr, (int(w * 0.06), int(h * 0.08), int(w * 0.22), int(h * 0.46)), (110, 85, 65))
    for row in range(3):
        yy = int(h * (0.14 + row * 0.10))
        _rect(dr, (int(w * 0.08), yy, int(w * 0.20), yy + int(h * 0.06)), (170 + row * 15, 140, 120))
    img.save(out, format="PNG")


def synth_dark_room(out: Path, w: int = 896, h: int = 672) -> None:
    img = Image.new("RGB", (w, h), (35, 32, 38))
    dr = ImageDraw.Draw(img)
    y_h = int(h * 0.56)
    _rect(dr, (0, y_h, w, h), (55, 48, 42))
    _rect(dr, (0, 0, w, y_h), (55, 52, 58))
    # single warm lamp
    lx, ly = int(w * 0.72), int(h * 0.34)
    dr.ellipse((lx - 40, ly - 40, lx + 40, ly + 40), fill=(255, 190, 120))
    dr.rectangle((lx - 8, ly + 40, lx + 8, int(h * 0.80)), fill=(70, 70, 72))
    # vague furniture in shadow
    _rect(dr, (int(w * 0.10), int(h * 0.52), int(w * 0.48), int(h * 0.78)), (70, 65, 62))
    img.save(out, format="PNG")


def main() -> None:
    root = _repo_root()
    dest = root / "dogfood-input"
    dest.mkdir(parents=True, exist_ok=True)
    synth_living_room(dest / "synth_living_cables.png")
    synth_bedroom(dest / "synth_bedroom_clutter.png")
    synth_desk_wfh(dest / "synth_desk_wires.png")
    synth_dark_room(dest / "synth_dark_lamp.png")
    print(f"Wrote PNGs under {dest}")


if __name__ == "__main__":
    main()
