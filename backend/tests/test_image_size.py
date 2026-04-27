"""image_pixel_size の回帰テスト。Pillow で生成した画像と照合。"""

from __future__ import annotations

import pytest
from PIL import Image

from image_size import MIN_SIDE_VLM, image_pixel_size


def test_png_matches_pillow(tmp_path) -> None:
    p = tmp_path / "a.png"
    im = Image.new("RGB", (64, 48), (10, 20, 30))
    im.save(p, "PNG")
    wh = image_pixel_size(str(p))
    assert wh == (64, 48)


def test_jpeg_matches_pillow(tmp_path) -> None:
    p = tmp_path / "a.jpg"
    im = Image.new("RGB", (100, 80), (200, 100, 50))
    im.save(p, "JPEG", quality=90)
    wh = image_pixel_size(str(p))
    assert wh == (100, 80)


def test_webp_vp8x_or_lossless_matches_pillow(tmp_path) -> None:
    p = tmp_path / "a.webp"
    im = Image.new("RGB", (120, 90), (255, 0, 0))
    im.save(p, "WEBP", lossless=True)
    wh = image_pixel_size(str(p))
    assert wh == (120, 90)
    assert min(wh) >= MIN_SIDE_VLM


def test_1x1_png_dimensions(tmp_path) -> None:
    p = tmp_path / "1.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(p, "PNG")
    wh = image_pixel_size(str(p))
    assert wh == (1, 1)
    assert min(wh) < MIN_SIDE_VLM
