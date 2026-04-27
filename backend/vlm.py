"""Ollama 上のローカルVLM（Qwen-VL系）による部屋画像分析。"""

from __future__ import annotations

import base64
import json
import os
import re
from typing import Any

import httpx

from prompt import ANALYZE_SYSTEM, build_user_prompt
from schema import RoomAnalysis, room_analysis_json_schema

_DEFAULT_BASE = "http://127.0.0.1:11434"
_OLLAMA_CHAT = f"{os.environ.get('OLLAMA_HOST', _DEFAULT_BASE).rstrip('/')}/api/chat"

def _timeout_seconds() -> float:
    # dogfooding では重いモデルで遅くなりがちなので、デフォルトを長めに
    return float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "600"))


def _read_image_b64(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    return base64.b64encode(raw).decode("ascii")


def _strip_fenced_json(s: str) -> str:
    t = s.strip()
    m = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", t, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return t


def _to_list_5(x: Any, default: str) -> list[str]:
    if x is None:
        return [default]
    if isinstance(x, str):
        s = x.strip()
        return [s] if s else [default]
    if isinstance(x, list):
        out: list[str] = []
        for i in x:
            s = str(i).strip()
            if s:
                out.append(s)
        if not out:
            return [default]
        return out[:5]
    return [str(x)][:1]


def _coerce_parsed_to_schema_shape(obj: Any) -> dict[str, Any]:
    d = obj if isinstance(obj, dict) else {}
    return {
        "room_type": str(d.get("room_type") or "判別困難（画像条件を要確認）").strip()
        or "判別困難（画像条件を要確認）",
        "style": str(d.get("style") or "判別困難").strip() or "判別困難",
        "problems": _to_list_5(
            d.get("problems"), "画像上の課題を十分に言語化できませんでした"
        ),
        "recommendations": _to_list_5(
            d.get("recommendations"), "採光・整線・収納の3点から優先的に改善を検討"
        ),
        "shopping_keywords": _to_list_5(
            d.get("shopping_keywords"), "部屋 インテリア 照明"
        ),
    }


def _parse_model_json(text: str) -> dict:
    t = _strip_fenced_json(text)
    return json.loads(t)


def analyze_room(
    image_path: str,
    *,
    style_target: str | None = None,
    budget: str | None = None,
    want_before_after: bool = False,
) -> dict:
    """
    部屋画像を Ollama / Qwen2.5-VL で分析し、RoomAnalysis 互換 dict を返す。

    環境変数:
    - OLLAMA_HOST: 例 http://127.0.0.1:11434
    - OLLAMA_MODEL: 例 qwen3-vl:8b / qwen2.5vl:7b（`ollama list` で表示される名前に合わせる）
    """
    # 既定は「新しめ優先」: qwen3-vl が入っていればそちら、無ければ qwen2.5vl
    model = os.environ.get("OLLAMA_MODEL") or "qwen3-vl:8b"
    user_content = build_user_prompt(style_target, budget, want_before_after)
    b64 = _read_image_b64(image_path)

    try:
        schema_fmt: dict | str = room_analysis_json_schema()
    except Exception:
        schema_fmt = "json"
    fmt: dict | str = schema_fmt

    payload: dict = {
        "model": model,
        "stream": False,
        "format": fmt,
        "options": {"temperature": 0.0},
        "messages": [
            {"role": "system", "content": ANALYZE_SYSTEM},
            {
                "role": "user",
                "content": user_content,
                "images": [b64],
            },
        ],
    }
    # thinking 設定はモデル/バージョンで挙動が変わるため、環境変数で明示したときのみ送る
    think_env = os.environ.get("OLLAMA_THINK")
    if think_env is not None:
        payload["think"] = think_env

    def _post_chat(p: dict) -> dict:
        with httpx.Client(timeout=_timeout_seconds()) as client:
            rr = client.post(_OLLAMA_CHAT, json=p)
            # model 未導入などで 404 の場合は、より軽い/旧世代へフォールバック
            if rr.status_code == 404 and os.environ.get("OLLAMA_MODEL") is None:
                p = {**p, "model": "qwen2.5vl:7b"}
                rr = client.post(_OLLAMA_CHAT, json=p)
            if rr.status_code == 400 and p.get("format") != "json":
                # 古い Ollama 等で JSON Schema の structured output が使えない場合
                p = {**p, "format": "json"}
                rr = client.post(_OLLAMA_CHAT, json=p)
            rr.raise_for_status()
            return rr.json()

    used_model = payload.get("model")
    data = _post_chat(payload)

    msg = data.get("message") or {}
    # 一部モデルは structured output を thinking 側に入れることがあるためフォールバック
    text = (msg.get("content") or msg.get("thinking") or msg.get("response") or "").strip()
    err_note: str | None = None
    raw_excerpt: str | None = None
    try:
        if not text:
            err_note = "empty_response"
            parsed = {}
        else:
            parsed = _parse_model_json(text)
    except (json.JSONDecodeError, TypeError) as e:
        err_note = f"json_parse: {e}"
        raw_excerpt = text[:800] if text else None
        parsed = {}

    # qwen3-vl が JSON を守らない場合は、互換モデルへ 1 回だけフォールバック
    if err_note and str(model).startswith("qwen3-vl"):
        fb_model = os.environ.get("OLLAMA_FALLBACK_MODEL", "qwen2.5vl:7b")
        fb_payload = {**payload, "model": fb_model, "format": schema_fmt}
        used_model = fb_model
        data = _post_chat(fb_payload)
        msg = data.get("message") or {}
        text = (msg.get("content") or msg.get("thinking") or msg.get("response") or "").strip()
        err_note = None
        raw_excerpt = None
        try:
            parsed = _parse_model_json(text) if text else {}
            if not text:
                err_note = "empty_response_fallback"
        except (json.JSONDecodeError, TypeError) as e:
            err_note = f"json_parse_fallback: {e}"
            raw_excerpt = text[:800] if text else None
            parsed = {}

    if not isinstance(parsed, dict):
        err_note = err_note or "response_not_object"
        parsed = {}

    coerced = _coerce_parsed_to_schema_shape(parsed)
    try:
        result = RoomAnalysis.model_validate(coerced)
    except Exception as e:
        d = coerced
        d["_error"] = err_note or f"validate: {e}"
        return d

    out = result.model_dump()
    out["_model_used"] = used_model
    if err_note:
        out["_raw_parse_warning"] = err_note
        if raw_excerpt:
            out["_raw_text_excerpt"] = raw_excerpt
    return out
