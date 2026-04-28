# dogfooding notes

## 目的

いろんな **ユーザー像（ペルソナ）** を参考に、同じ部屋画像でも `style/budget/before_after` を変えて VLM 出力がどう変化するかを記録する。

## 重要（コミットしない）

- 実部屋写真は個人情報・プライバシーになりうるため **コミットしない**。  
  画像は `/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/dogfood-input/` に置き、`.gitignore` 済み。
- バッチ実行でできる **`notes/dogfooding/` の個別レポート（`*.md`）も既定では Git に含めない**（ルート `.gitignore`）。まとめの `index.md` と本 README だけ追跡対象にできる。

## 使い方

### 1コマンド（おすすめ）

```bash
cd /media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner
# 画像を dogfood-input/ に入れた後
OLLAMA_MODEL=qwen3-vl:4b bash backend/run-dogfood.sh
```

1. ペルソナ定義（JSON）を確認/編集:
   - `/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/dogfooding/personas.json`
2. 入力画像を置く（コミット禁止）:
   - `/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/dogfood-input/`
3. バッチ実行（Ollama 起動済み、`OLLAMA_MODEL` 任意）:

```bash
cd /media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/backend
source .venv/bin/activate
python dogfood.py --images dogfood-input --personas dogfooding/personas.json --out notes/dogfooding
```

出力: `notes/dogfooding/*.md`（1画像×1ペルソナ=1ファイル）。

4. まとめ（index）生成:

```bash
cd /media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/backend
source .venv/bin/activate
python dogfood_index.py --dir notes/dogfooding
```

出力: `notes/dogfooding/index.md`

## 推奨ワークフロー

- 実写が無い場合は合成PNGを生成できる: `python scripts/gen_dogfood_synthetic_images.py`（`dogfood-input/` に出力。要 Pillow）
- フロントから同じフローを叩く: `cd frontend && npm run dogfood`（`backend/run-dogfood.sh` を実行）
- まず `dogfood-input/` に **PNG/JPEG/WebP** を置く（SVG はモデルが失敗しやすいので避ける）
- `python dogfood.py ...` を実行
- 生成された `.md` の「結論」を埋め、`prompt.py` 変更→再実行で差分比較

## 記録フォーマット

各レポートは以下を含む:

- 結論
- 確認済み事実
- 未確認/要確認項目
- 次アクション

