# Contributing

Issues と Pull Request を歓迎します。

## 開発の流れ

1. 変更はできるだけ **小さく・目的が一つ** に絞るとレビューしやすいです。
2. バックエンドを触ったら:

   ```bash
   cd backend && ./run-tests.sh
   ```

3. フロントを触ったら:

   ```bash
   cd frontend && npm run build
   ```

   （ルートから `npm run dev` で API と Next を同時起動して手動確認でも構いません。）

4. UI のスクショは `npm run screenshot` で `docs/assets/screenshot.png` を更新できます（Playwright、API 不要）。

## プロンプト・VLM まわり

- 文言の調整は `backend/prompt.py`。
- 実写や合成画像での試行は `notes/dogfooding/` の手順（`backend/run-dogfood.sh`）を参照。個人の部屋写真は **コミットしない** でください（`.gitignore` の `dogfood-input/`）。

## ライセンス

コントリビューションは [MIT](LICENSE) と同じ条件で提供されるものとみなします。
