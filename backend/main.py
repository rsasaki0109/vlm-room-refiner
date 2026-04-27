"""FastAPI: 部屋画像分析 REST API。"""

from __future__ import annotations

import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from image_size import MIN_SIDE_VLM, image_pixel_size
from vlm import analyze_room


def _max_image_bytes() -> int:
    return int(os.environ.get("MAX_IMAGE_BYTES", str(8 * 1024 * 1024)))


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    # temp files use delete=False handled by OS / small footprint


app = FastAPI(
    title="vlm-room-refiner",
    description="部屋画像 → Ollama(Qwen2.5-VL) による改善提案JSON",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(..., description="部屋の画像 (JPEG/PNG 等)"),
    style: str | None = Form(None, description="目標の雰囲気 (任意、例: ミニマル)"),
    budget: str | None = Form(None, description="予算感 (任意)"),
    before_after: bool = Form(
        False, description="Before/After 的な文を入れてよい (任意)"
    ),
) -> dict[str, Any]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="画像ファイル (image/*) をアップロードしてください"
        )
    suffix = os.path.splitext(file.filename or "")[1] or ".jpg"
    if suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"):
        suffix = ".jpg"
    name = f"{uuid.uuid4().hex}{suffix}"
    path = os.path.join(tempfile.gettempdir(), f"room-refiner-{name}")
    try:
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="空のファイルです")
        lim = _max_image_bytes()
        if len(data) > lim:
            raise HTTPException(
                status_code=413,
                detail=f"画像サイズが大きすぎます（最大おおよそ{lim // (1024 * 1024)}MB）。大きい画像は縮小して再アップロードしてください。",
            )
        with open(path, "wb") as f:
            f.write(data)
        wh = image_pixel_size(path)
        if wh is not None:
            w, h = wh
            if min(w, h) < MIN_SIDE_VLM:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"画像の短辺が短すぎます（{w}×{h} px）。"
                        f"Ollama の Qwen2.5-VL では少なくとも短辺{MIN_SIDE_VLM}px 以上推奨です。"
                    ),
                )
        try:
            return analyze_room(
                path,
                style_target=style,
                budget=budget,
                want_before_after=before_after,
            )
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            raise HTTPException(
                status_code=503, detail=f"Ollama に接続できません: {e!s}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502, detail=f"Ollama がエラーを返しました: {e!s}"
            ) from e
    finally:
        if os.path.isfile(path):
            try:
                os.unlink(path)
            except OSError:
                pass
