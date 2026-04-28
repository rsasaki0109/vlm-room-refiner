# experiments

ロードマップと「いま何を優先するか」の **統合計画** は [PLAN.md](./PLAN.md)。本ファイルは **日付付きの実験ログ**として追記していく。

## 2026-04-27

### 起動

- `backend`: `cd` して `uvicorn main:app --host 0.0.0.0 --port 8000`（`backend` をカレントに。依存は `requirements.txt` + venv 推奨）
- `frontend`: `cd frontend && npm run dev`（`NEXT_PUBLIC_API_BASE` は `.env.local` 参照）
- Ollama: `ollama run qwen2.5vl:7b` でモデル有無の確認。未 pull の場合は `ollama pull qwen2.5vl:7b`（例）

### 環境変数（バックエンド）

| 変数 | 既定 | 説明 |
|------|------|------|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama ベース URL |
| `OLLAMA_MODEL` | `qwen2.5vl:7b` | 実在するモデル名に合わせる（`ollama list`） |
| `CORS_ORIGINS` | ローカル 3000 | カンマ区切りで追加可能 |

### 事実

- 実装時点のスナップショットでは **ホスト上の Ollama (`127.0.0.1:11434`) に接続不能** だった。推論 E2E は、Ollama 起動後に再試行が必要。

### 次

- 実機で `ollama` 起動 + モデル pull 後、`curl` で `/health`、小さい JPEG で `POST /analyze` を実行してログを追記。
- モデル名の差異（`qwen2.5-vl:7b` 等）で `404` になる場合は `OLLAMA_MODEL` を揃える。

## 2026-04-27（追記）一括起動

### 事実

- リポジトリ直下に `package.json` を置き `concurrently` で `npm run dev` 可能にした。API 既定は **8010**（`API_PORT` で上書き）。フロントの `NEXT_PUBLIC_API_BASE` 未設定時は `http://127.0.0.1:8010` に合わせた（`/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/frontend/app/page.tsx`）。
- Ollama は引き続き本環境では接続不能（`verify-ollama.sh` も 200 にならない想定）。推論 E2E はデーモン起動後。

### 次

- ホストで `ollama serve` 相当を起動 → `bash /media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/scripts/verify-ollama.sh` が OK か確認 → `ollama pull` で `OLLAMA_MODEL` に合うタグを用意 → `API_PORT=8010` で `POST /analyze` の本文をここに貼る。

## 2026-04-27 E2E（自ホストで実行した結果）

### 結論

- Ollama を起動 → `qwen2.5vl:7b` を pull 済み想定に合わせ → バックエンド（`http://127.0.0.1:8010`）に対し **有効寸法の合成 PNG（640×480）** を POST したところ **`HTTP 200` と所望 JSON** を得た。  
- **1×1 や極小 PNG** は、Ollama 側 `qwen25vl` 画像前処理（`width/height` が要因 28 未満）で **500 / パニック** になった。テスト用画像は短辺 **少なくとも 28px 超** 推奨（実測は `process_image.go` 由来の制約）。

### 確認済み事実

- `ollama serve` 起動後、API `OLLAMA_HOST` / `OLLAMA_MODEL=qwen2.5vl:7b`、Python venv 上の `uvicorn`（`backend`）を使用。
- 成功例（応答抜粋。キー名は本リポ `RoomAnalysis` 準拠）:

```json
{
  "room_type": "小規模住居系",
  "style": "シンプル",
  "problems": [
    "配線: 配線が見えないため、配線の隠し方や整理が必要。",
    "収納: 収納スペースが見当たらないため、収納家具の導入を検討。",
    "採光: 画像からは窓が見えないため、採光の改善が必要。",
    "配色: ベージュとベージュの重ね合わせで単調感があり、色の変更を検討。",
    "家具サイズ感: フロアが見えないため、家具のサイズ感が不明。"
  ],
  "recommendations": [
    "収納家具の導入",
    "窓の設置",
    "色の変更",
    "家具のサイズ感を考慮した配置",
    "配線の隠し方"
  ],
  "shopping_keywords": [
    "収納家具",
    "窓",
    "色",
    "家具サイズ",
    "配線隠し"
  ]
}
```

- 失敗例: 1×1 PNG では Ollama ログに `height:1 or width:1 must be larger than factor:28`（または従来の `png: invalid format` 相当）が出る。合成の乱数点画像 640×480 では Ollama `POST /api/chat` 約 3.1s で完了。

### 次アクション

- フロントで短辺チェック（任意。現状 API が弾く）。他形式（HEIC 等）の扱いは要検討。  
- 上記 E2E 用に起動した `ollama serve` / `uvicorn` は、記録後 **停止済み**（`11434` / `8010` 未応答を確認）。利用時は改めて起動。

### 追記：API 側の解像度チェック

- `POST /analyze` は PNG/JPEG/WebP（`RIFF...WEBP` 先頭、VP8X/VP8L/VP8）を標準ライブラリで解像度推定できた場合、**短辺 32px 未満**を **HTTP 400**、**本文サイズ**（既定 8MB）超過を **HTTP 413**（`MAX_IMAGE_BYTES` 環境で変更可。`backend/main.py` / `backend/image_size.py`）。
- 他形式（GIF 等）や寸法取れない場合は Ollama に任せ、失敗しうる。フロントは 8MB 超の事前弾きと、400/413/502/503 の**見出し＋本文＋ HTTP** 表示（`frontend/app/page.tsx`）。
- 回帰テスト: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` を付与（本環境は ROS 由来の `pytest` エントリポイント衝突回避）。`backend/run-tests.sh` または同様の環境付き `python -m pytest tests`。

## 2026-04-27 Dogfooding（qwen3-vl）

### 結論

- **qwen3-vl:4b** を導入し、`POST /analyze` を実行して **HTTP 200** で JSON を取得できた。
- `style=韓国風` / `budget=1万円前後` / `before_after=true` を与えると、recommendations に **Before/After 文**が混ざる形で返ってきた。

### 確認済み事実

- Ollama: `http://127.0.0.1:11434`
- Model: `qwen3-vl:4b`（`ollama pull qwen3-vl:4b`）
- API: `uvicorn main:app --port 8010`
- テスト入力: 640×480 の合成 PNG（短辺 32px 以上）

成功レスポンス（抜粋）:

```json
{
  "room_type": "1Kマンションのリビング",
  "style": "ミニマルな韓国風",
  "problems": [
    "配色がベージュとグレーの単色で、空間に奥行きがなく、視覚的に退屈。",
    "収納スペースが不足し、小物が散らばっている。",
    "采光が悪く、明るさが足りない。",
    "ファブリックの色が暗く、清潔感が欠如。",
    "ファブリックのサイズが大きすぎて、バランスが崩れている。"
  ],
  "recommendations": [
    "Before: ... After: ...",
    "Before: ... After: ...",
    "Before: ... After: ...",
    "Before: ... After: ...",
    "Before: ... After: ..."
  ],
  "shopping_keywords": [
    "木目調のミニマリストテーブル 10000円以内",
    "韓国風の布団 10000円以内",
    "シンプルな収納ボックス 10000円以内",
    "明るい色のファブリック 10000円以内",
    "シンプルなライト 10000円以内"
  ]
}
```

### 未確認/要確認項目

- recommendation の日本語品質（誤字「退苦」など）や、実画像での安定性。
- `qwen3-vl:8b` に上げた時の質/レイテンシ差。

### 次アクション

- 実部屋写真で同じパラメータ（style/budget/before_after）を試し、差分を記録する。
- 誤字・抽象表現が出やすい場合は `prompt.py` の制約文言を強化する。

| 本ファイルの絶対パス |
|----------------------|
| `/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/docs/experiments.md` |
