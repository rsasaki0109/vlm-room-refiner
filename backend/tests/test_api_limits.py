"""API のファイルサイズ・画像種別の制約。"""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from main import app


def _img_bytes(fmt: str = "PNG", size: tuple[int, int] = (40, 40)) -> bytes:
    buf = io.BytesIO()
    im = Image.new("RGB", size, (1, 2, 3))
    im.save(buf, fmt)
    return buf.getvalue()


@patch.dict("os.environ", {"MAX_IMAGE_BYTES": "200"}, clear=False)
def test_413_too_large() -> None:
    c = TestClient(app)
    big = b"0" * 2000
    r = c.post(
        "/analyze",
        data={"before_after": "false"},
        files={"file": ("x.png", big, "image/png")},
    )
    assert r.status_code == 413
    assert "大き" in (r.json().get("detail") or "")


@patch("main.analyze_room", return_value={"room_type": "x", "style": "y", "problems": ["a"], "recommendations": ["b"], "shopping_keywords": ["c"]})
def test_200_on_valid_png(_mock) -> None:
    c = TestClient(app)
    b = _img_bytes()
    r = c.post(
        "/analyze",
        data={"before_after": "false"},
        files={"file": ("room.png", b, "image/png")},
    )
    assert r.status_code == 200, r.text
