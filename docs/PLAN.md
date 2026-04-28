# vlm-room-refiner — 開発計画・ロードマップ（統合）

本ファイルは、散在していた「次に何をするか」「どこまでが MVP か」「品質をどう上げるか」を **1 本に集約**したマスター計画です。個別の技術メモは [architecture.md](./architecture.md)・[prompts.md](./prompts.md)・[experiments.md](./experiments.md) を参照し、**日付ログは experiments に残し、方針の正本は本書**とする。

---

## 1. プロジェクトの狙い

| 観点 | 内容 |
| --- | --- |
| **ユーザー価値** | 部屋写真から「課題 → 改善案 → 買い物の検索語」を一度に得る |
| **プライバシー** | 画像をクラウドの一般向け Vision API に送らず、**ローカル（Ollama + Qwen-VL 系）**で完結させる |
| **機械可読** | JSON（`room_type` / `style` / `problems` / `recommendations` / `shopping_keywords`）で後続アプリに繋げやすい |
| **実用トレードオフ** | 完璧なインテリア監修より **「手が動く・検索に繋がる」具体性** を優先し、[プロンプト](../backend/prompt.py) と dogfooding で継続改善する |

### MVP の境界（現時点）

**含む:**

- FastAPI `POST /analyze`（画像検証・Ollama 呼び出し・Pydantic 検証）
- Next.js の LP／デモ UI・エラー表示（GitHub Pages はモック）
- CLI・構造化出力フォールバック（JSON Schema → `format: json`）
- CI（フロント `build`・バックエンド `pytest`）

**含まない（意図的に後回し）:**

- ユーザー認証・マルチテナント
- クラウドホスティング前提のスケール設計
- 実売データベースや EC 直結

---

## 2. 現状サマリ（2026-04 時点）

| 領域 | 状態 |
| --- | --- |
| **ランタイム** | Ollama `POST /api/chat`、既定モデルは環境変数（コード側既定は `qwen3-vl:8b`、未取得時や JSON 失敗時は `qwen2.5vl:7b` などフォールバック） |
| **入力検証** | JPEG/PNG/WebP、短辺 **32px 未満** は 400、サイズ上限は既定 **8MB**（413） |
| **プロンプト** | 賃貸・工事回避・具体品目を強める方向で反復調整済み（詳細は [prompts.md](./prompts.md) と `backend/prompt.py`） |
| **検証** | [notes/dogfooding/README.md](../notes/dogfooding/README.md) のペルソナ × 画像バッチ、`dogfood_index.py` で index 集計 |
| **公開** | GitHub Pages で UI デモ（モック API）、README にライセンス・Contributing・Issue テンプレ |

---

## 3. アーキテクチャ要約

詳細は [architecture.md](./architecture.md)。ここでは計画に効く要点のみ。

```
Browser ──POST /analyze──► FastAPI ──POST /api/chat──► Ollama (Qwen-VL)
                               │
                               └── Pydantic で RoomAnalysis 検証
```

- **API 既定ポート 8010**（他サービスと被りにくくするため）。ルート `npm run dev` で API と Next を同時起動。
- **構造化出力**: Ollama の `format` に JSON Schema を渡し、拒否時は `json` モードへ。
- **テスト**: `backend/tests/`、`./run-tests.sh` でプラグイン自動読込を無効化（ROS 等との衝突回避）。

---

## 4. 品質・プロンプト戦略

### 4.1 方針の正

- ソース: [`backend/prompt.py`](../backend/prompt.py)
- 説明の索引: [prompts.md](./prompts.md)

### 4.2 継続的に潰す失敗モード

優先度の高い順に、モデル出力で繰り返し問題になるパターン:

1. **工事・開口・リフォーム級**（窓増設、壁穴、フローリング張替え等）→ 禁止語・賃貸向け代替を強調
2. **抽象的 recommendations**（「色を変える」「収納を増やす」のみ）→ 具体アイテム必須の制約
3. **窓の有無の断定**（写真に写っていないのに「窓がない」）→ 「自然光が弱く見える」等へ
4. **鏡・反射で採光を補う表現**が「窓の位置」などの誤仮定を誘発 → 床置き姿見・貼ってはがせるミラー等に限定
5. **JSON 破損**（特に qwen3-vl）→ パースフォールバック・別モデル 1 回リトライ・`temperature` 低め

### 4.3 検証ループ（Dogfooding）

| 項目 | 内容 |
| --- | --- |
| **入力** | `dogfood-input/` に画像（**実写はコミットしない**。合成は `scripts/gen_dogfood_synthetic_images.py` 可） |
| **ペルソナ** | [`dogfooding/personas.json`](../dogfooding/personas.json) |
| **実行** | `bash backend/run-dogfood.sh` または `npm run dogfood` |
| **成果物** | `notes/dogfooding/*.md`（個別レポートは `.gitignore`、README と `index.md` のみ追跡可） |
| **集計** | `backend/dogfood_index.py` → `notes/dogfooding/index.md` の flags で工事っぽい語をざっくり検出 |

---

## 5. 実験ログとの役割分担

- **[experiments.md](./experiments.md)**: **日付付きの時系列ログ**（起動手順のスナップショット、当時の `OLLAMA_MODEL`、curl 結果の貼り付け）。**削らず追記**する。
- **本 PLAN**: **「いま何を優先し、何をやらないか」** の更新先。ロードマップの意思決定が変わったら **本書を直す**。

---

## 6. ロードマップ（フェーズ）

### Phase A — 完了（MVP + 運用基盤）

- [x] FastAPI + Ollama + 構造化 JSON
- [x] Next.js UI・GitHub Pages デモ（モック）
- [x] 画像サイズ・形式検証・HTTP ステータス整理
- [x] CI（frontend build + pytest）
- [x] Dogfooding スクリプトと index
- [x] LICENSE / README / CONTRIBUTING / Issue・PR テンプレ
- [x] プロンプト反復（賃貸・具体性・禁止系）

### Phase B — 進行中（品質・再現性）

- [ ] **実写**でのプロンプト調整（個人写真はコミットしない）と、効いた差分を `experiments.md` または dogfooding レポートに記録
- [ ] **モデル比較**: `qwen3-vl:8b` / `4b` / `qwen2.5vl:7b` の品質・レイテンシ・JSON 遵守率の表を `experiments.md` に追記
- [ ] **フロント**: 短辺・ファイルサイズの事前チェックは一部済み。API エラー文言との二重表示の整理（任意）
- [ ] **npm audit** の moderate 依存の精査（破壊的変更なしで直せる範囲）

### Phase C — 本番寄り（必要になったら）

- [ ] アップロード前の **長辺リサイズ**（縮小のみ・EXIF の扱いを決める）
- [ ] **レート制限**・ペイロード上限の運用値
- [ ] **認証**（公開インスタンスを作る場合のみ）
- [ ] スタイル・予算の **UI プリセット**と API の一貫性（LP のプリセットと API パラメータの対応表）

### Phase D — 将来のアイデア（優先度低）

- HEIC 等の追加フォーマット（ライセンス・依存を確認のうえ）
- 出力の多言語化
- 同一画像の Before/After **画像**生成（別モデル・別プロジェクト扱いが現実的）

---

## 7. 技術的制約・既知リスク

| 項目 | 内容 |
| --- | --- |
| **画像寸法** | VLM 実装により **極小画像は 500 や前処理エラー**になりうる。API は短辺 32px 未満を拒否。実験メモ: [experiments.md](./experiments.md) |
| **モデル差** | Qwen3-VL は JSON を崩しやすい場合があり **フォールバック**に依存。運用では `OLLAMA_MODEL` と `OLLAMA_FALLBACK_MODEL` を明示推奨 |
| **幻覚** | 「窓を設置」等はプロンプトだけでは完全防止できない。**ログと flags で監視**し続ける |
| **ROS pytest** | グローバルプラグイン衝突 → `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`（`run-tests.sh` 済み） |

---

## 8. ドキュメント索引

| ファイル | 役割 |
| --- | --- |
| [README.md](../README.md) | クイックスタート・環境変数・バッジ |
| **本 PLAN.md** | **開発計画・ロードマップの正本** |
| [architecture.md](./architecture.md) | 構成・通信・テスト |
| [prompts.md](./prompts.md) | プロンプト構造の索引 |
| [experiments.md](./experiments.md) | 実験・日付ログ |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | PR・テストの作法 |
| [notes/dogfooding/README.md](../notes/dogfooding/README.md) | バッチ検証の手順 |

---

## 9. 次アクション（短期チェックリスト）

実装に着手するときは、次を順に確認する:

1. Ollama が起動し、`ollama list` に狙いのタグがあるか
2. `curl http://127.0.0.1:8010/health` が OK か（`npm run dev` 後）
3. 変更がプロンプトなら **dogfood 1 ケース**で回帰確認
4. `backend/./run-tests.sh` と `frontend/npm run build`
5. 時系列の詳細データは **experiments.md に追記**、優先度の変更は **本 PLAN を更新**

---

| 本ファイルの参照パス |
| --- |
| `/media/sasaki/aiueo/ai_coding_ws/vlm-room-refiner/docs/PLAN.md` |
