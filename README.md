# vlm-room-refiner

部屋の写真を **Ollama 上の Qwen2.5-VL**（ローカル VLM）に渡し、**部屋タイプ・スタイル・課題・改善案・購入用キーワード**を JSON で返す Web＋API です。完璧な精度は狙わず、プロンプト改善で育てる前提の MVP です。

| 層 | 技術 |
|----|------|
| API | Python 3.12+ / FastAPI / httpx / Pydantic v2 |
| UI | Next.js 15 / React 19 / Tailwind |
| 推論 | Ollama `POST /api/chat`、既定モデル名は環境で指定 |

## 必要なもの

- [Ollama](https://ollama.com/) が起動し、推論用に **Qwen2.5-VL 系**（例: `qwen2.5vl:7b`）が `ollama list` に出ていること
- **Node.js**（例: 20+）と **npm**
- **Python 3.12+**（API 用。`backend` に venv を作る想定）

## クイックスタート

### 1. モデル（未導入なら）

```bash
ollama pull qwen2.5vl:7b
# 表示名は環境に合わせ、必要なら OLLAMA_MODEL を後述の表で変更
```

### 2. 依存のインストール

リポジトリ根:

```bash
cd /path/to/vlm-room-refiner
npm install
cd frontend && npm install && cd ..
```

API 用 venv（初回）:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows は .venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 3. 一括で開発起動

Ollama を起動した状態で、**リポジトリ根**から:

```bash
npm run dev
```

- **API**: 既定 `http://127.0.0.1:8010`（`8000` は他プロセスと被りやすいため。`API_PORT` で変更可）
- **Web**: `http://localhost:3000`
- フロントの API 向き先: 未設定なら `http://127.0.0.1:8010`。変えたい場合は `frontend/.env.local` を `frontend/.env.local.example` からコピーして編集

### 4. 動作確認

```bash
curl -sS http://127.0.0.1:8010/health
# {"status":"ok"}
```

## 環境変数（主に API / 推論）

| 変数 | 既定 | 意味 |
|------|------|------|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama のベース URL |
| `OLLAMA_MODEL` | `qwen2.5vl:7b` | 利用するタグ名（`ollama list` と揃える） |
| `MAX_IMAGE_BYTES` | `8388608`（8MB） | 1 リクエストの画像バイト数上限（超過は 413） |
| `CORS_ORIGINS` | ローカル 3000 系 | カンマ区切りで追記可 |
| `API_PORT` | `8010` | ルート `npm run dev` の API 用（`scripts/run-api.sh`） |

## API

| メソッド | パス | 説明 |
|----------|------|------|
| `GET` | `/health` | 生存確認 |
| `POST` | `/analyze` | `multipart/form-data` の `file`（画像）＋任意 `style` / `budget` / `before_after` |

- 極小画像（短辺 32px 未満で、PNG/JPEG/WebP として寸法を取れた場合）は **400**。寸法が取れない形式は Ollama 側の制約に委ねる。
- Ollama 未起動などは **503**、Ollama が 5xx を返す場合は **502** など。

## CLI

```bash
cd backend
source .venv/bin/activate
python cli.py /path/to/room.jpg --style ミニマル
```

## テスト

```bash
cd backend
./run-tests.sh
```

ROS 等でグローバル `pytest` プラグインが衝突する場合は、スクリプト内の `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` を踏襲する。依存は `requirements-dev.txt`（Pillow / pytest。本番 `requirements.txt` には含めない）。

## CI（GitHub Actions）

`main` / `master` へのプッシュと PR で、次のジョブが **Ubuntu** 上で走ります（Ollama は不要）。

| ジョブ | 内容 |
|--------|------|
| `frontend` | `frontend` で `npm ci` → `npm run build` |
| `backend` | `backend` で `pip install -r requirements-dev.txt` → `pytest tests/`（`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`） |

定義ファイル: `.github/workflows/ci.yml`。リモートにプッシュすると Actions タブから結果を確認できる。

## リポジトリ構成

```text
vlm-room-refiner/
  README.md                 # 本ファイル
  package.json              # ルート: npm run dev など
  .github/workflows/ci.yml  # GitHub Actions
  scripts/                  # run-api.sh, verify-ollama.sh
  backend/
    main.py                 # FastAPI
    vlm.py                  # Ollama 呼び出し
    prompt.py, schema.py, image_size.py, cli.py
    requirements.txt
    requirements-dev.txt
    run-tests.sh, pytest.ini, tests/
  frontend/                 # Next.js（app ルーター）
  docs/
    architecture.md
    prompts.md
    experiments.md
```

## ドキュメント

設計・プロンプト原文・実験メモは `docs/` を参照。絶対パスで相互参照する場合の例:  
`/path/to/vlm-room-refiner/docs/architecture.md`

## 今後の候補

- 実部屋写真でのプロンプト微調整と `docs/experiments.md` への追記
- 本番想定: レート制限、認証、長辺リサイズ（アップロード前の軽量処理）

## ライセンス

未設定（必要に応じて追記してください）。
