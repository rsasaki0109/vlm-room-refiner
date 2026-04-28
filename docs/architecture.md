# architecture

開発の優先度・ロードマップ・品質方針の **正本** は [PLAN.md](./PLAN.md)。

## 目的

部屋の画像を入力として、ローカル VLM（Ollama 上の Qwen2.5-VL）が **部屋タイプ / スタイル / 課題 / 改善案 / 購入用キーワード** を JSON で返す。

## 構成

| 層 | 役割 | 主な技術 |
|----|------|----------|
| Frontend | 画像アップロード、結果の整形表示、任意のスタイル・予算 | Next.js 15 (App Router), React 19, Tailwind |
| Backend | `multipart/form-data` 受信、一時保存、Ollama 呼び出し、レスポンス検証 | FastAPI, httpx, Pydantic v2 |
| 推論 | 画像+テキスト、JSON 出力 | Ollama `POST /api/chat`、環境で指定したモデル名 |

## 通信

- ブラウザ → `POST {NEXT_PUBLIC_API_BASE}/analyze`（フロントの未設定時は `http://127.0.0.1:8010`＝ルート `npm run dev` と揃えた既定）
- Backend → `POST {OLLAMA_HOST}/api/chat`（デフォルト `http://127.0.0.1:11434`）

CORS: `CORS_ORIGINS` 環境変数（カンマ区切り）。未設定時は `localhost:3000` 系。

## 出力

`RoomAnalysis`（Pydantic）のフィールド。Ollama 側は可能な限り `format` に JSON Schema（`RoomAnalysis.model_json_schema()`）を渡し、失敗した場合は `format: "json"` にフォールバックする（`/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/backend/vlm.py`）。

## CLI

`backend/cli.py` で同一ロジックを呼び、標準出力に JSON。実験や E2E の補助用。

| 絶対パス |
|----------|
| `/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/backend/cli.py` |

## ルート一括起動

リポジトリ直下で `npm install` 後 `npm run dev` すると、**API（`API_PORT` 未指定時 8010）** と **Next（3000）** を同時起動する。`8000` 番は他アプリと衝突しやすいため、既定 API ポートを 8010 にしている（`/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/package.json` / `scripts/run-api.sh`）。

Ollama 接続の目安: `bash scripts/verify-ollama.sh`（`OLLAMA_HOST` 可変）。

## テスト

- `cd backend` し、`./run-tests.sh`（`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` 付与、ROS 等のグローバル pytest プラグイン衝突回避。依存は `requirements-dev.txt`）。
- 中身: `image_pixel_size`（PNG/JPEG/WebP 寸法照合、Pillow 生成物と比較）、`POST /analyze` の大きいファイル 413・正常系のモック。

## 注意（Qwen2.5-VL / ollama）

極小画像（例: 1×1 px）は、Ollama ビルドの `qwen25vl` 前処理で **失敗** しうる。実機では少なくとも **短辺が数十 px 超** である必要がある（`docs/experiments.md` の 2026-04-27 E2E 参照）。
