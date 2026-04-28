# prompts

プロンプトの進め方・失敗モードの優先度は [PLAN.md](./PLAN.md) の「品質・プロンプト戦略」を参照。

## システム

```text
あなたは熟練のインテリアコーディネーターです。...
```

出所: `backend/prompt.py` の `ANALYZE_SYSTEM`。

## ユーザ（本文）

```text
この部屋の画像を分析し、与えられたJSONスキーマに厳密に従うキーのみを出力してください。

次の方針で埋めてください:
- room_type: ...
- style: ...
- problems: ...
- recommendations: ...
- shopping_keywords: ...
```

`build_user_prompt()` により、以下を任意追記可能:

- **目標の雰囲気**（`style` フォーム / `--style`）
- **予算感**（`budget` / `--budget`）
- **Before/After 指示**（`before_after` / `--before-after`）

上記の全文は同ファイル内の定数 `ANALYZE_USER_TEMPLATE` および `build_user_prompt` を参照。

| 絶対パス |
|----------|
| `/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/backend/prompt.py` |
