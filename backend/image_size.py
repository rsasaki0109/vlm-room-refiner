"""画像の解像度を推定（PNG/JPEG/WebP、標準ライブラリのみ。失敗したら None）。"""

from __future__ import annotations

_READ = 2 * 1024 * 1024

# ollama qwen25vl: SmartResize で短辺が要因 28 未満のとき失敗する例を踏まえ余裕
MIN_SIDE_VLM = 32


def image_pixel_size(path: str) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        b = f.read(_READ)
    if b.startswith(b"\x89PNG\r\n\x1a\n"):
        return _png_ihdr(b)
    if len(b) >= 2 and b[0:2] == b"\xff\xd8":
        return _jpeg_sof(b)
    if b.startswith(b"RIFF") and b[8:12] == b"WEBP":
        return _webp_riff(b)
    return None


def _webp_riff(b: bytes) -> tuple[int, int] | None:
    n = len(b)
    p = 12
    while p + 8 <= n:
        tag = b[p : p + 4]
        ch = int.from_bytes(b[p + 4 : p + 8], "little")
        body = p + 8
        ex = ch + (ch & 1)
        if body + ex > n:
            break
        d = b[body : body + ch]
        if tag == b"VP8X" and ch >= 10:
            w = 1 + int.from_bytes(d[4:7], "little")
            h = 1 + int.from_bytes(d[7:10], "little")
            return w, h
        if tag == b"VP8L" and ch >= 5 and d[0] == 0x2F:
            # 0x2F の次の 4 バイト (LE) の下位 14+14 bit が (w-1),(h-1)
            b = int.from_bytes(d[1:5], "little")
            w = 1 + (b & 0x3FFF)
            h = 1 + ((b >> 14) & 0x3FFF)
            if w and h:
                return w, h
        if tag == b"VP8 " and ch >= 10:  # lossy keyframe; sync
            if d[0:3] == b"\x9d\x01\x2a":
                w = (d[6] | (d[7] << 8)) & 0x3FFF
                h = (d[4] | (d[5] << 8)) & 0x3FFF
                if w and h:
                    return w, h
        p += 8 + ex
    return None


def _png_ihdr(b: bytes) -> tuple[int, int] | None:
    i = 8
    n = len(b)
    while i + 16 <= n:
        ln = int.from_bytes(b[i : i + 4], "big")
        t = b[i + 4 : i + 8]
        if t == b"IHDR" and ln >= 13 and i + 8 + 16 <= n:
            w = int.from_bytes(b[i + 8 : i + 12], "big")
            h = int.from_bytes(b[i + 12 : i + 16], "big")
            return w, h
        if ln <= 0 or i + 8 + ln > n:
            break
        i += 8 + ln
    return None


def _jpeg_sof(b: bytes) -> tuple[int, int] | None:
    if b[0:2] != b"\xff\xd8":
        return None
    i = 2
    n = len(b)
    while i + 4 < n:
        if b[i] != 0xFF:
            i += 1
            continue
        m = b[i + 1]
        if m == 0xD9:
            break
        if i + 3 >= n:
            break
        seg = int.from_bytes(b[i + 2 : i + 4], "big")
        if m in (0xC0, 0xC1, 0xC2) and seg >= 8 and i + 9 < n:
            h = int.from_bytes(b[i + 5 : i + 7], "big")
            w = int.from_bytes(b[i + 7 : i + 9], "big")
            return w, h
        i += 2 + seg
    return None
