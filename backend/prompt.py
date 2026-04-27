"""VLM 向けシステム／ユーザープロンプト。"""

ANALYZE_SYSTEM = """あなたは熟練のインテリアコーディネーターです。画像に写っている部屋の現状を観察し、\
具体的で実行可能な提案に落とし込みます。抽象的な言い回しは避け、部屋のレイアウト・配色・物の置き方に触れてください。"""

ANALYZE_USER_TEMPLATE = """この部屋の画像を分析し、与えられたJSONスキーマに厳密に従うキーのみを出力してください。

次の方針で埋めてください:
- room_type: 部屋の用途が推定できる範囲で具体的に（曖昧な「居室」は避け、分からなければ「小規模住居系」と理由を含めて短く）
- style: 画像から読み取れる要素に基づき、スタイルを名付けて推定
- problems: 視認できる問題を最大5件。各項目1文で、配線、収納、採光、配色、家具サイズ感など
- recommendations: 最大5件。掃除の指示だけにせず、レイアウト・小物の追加・色の調整など
- shopping_keywords: 各項目は検索用の短いフレーズ。商品カテゴリ＋特徴が分かるように

制約:
- 日本語
- 各配列は1〜5要素
- 推測に根拠が薄いことは、短く「仮定：」で明示
"""


def build_user_prompt(
    style_target: str | None = None,
    budget: str | None = None,
    want_before_after: bool = False,
) -> str:
    """拡張用: 目標スタイル・予算・Before/After を任意で追記。"""
    parts = [ANALYZE_USER_TEMPLATE.rstrip()]

    if style_target and style_target.strip():
        parts.append(
            f"\n【目標の雰囲気】ユーザーは「{style_target.strip()}」に近づけたい。可能な範囲で recommendations / shopping_keywords に反映。"
        )
    if budget and budget.strip():
        parts.append(
            f"\n【予算感】{budget.strip()}。無理のない価格帯を shopping_keywords / recommendations に意識。"
        )
    if want_before_after:
        parts.append(
            "\n【補足】recommendations の中に、現状（Before）と目指す完成イメージ（After）を一文ずつ入れる等、対比が分かる表現を1件以上含めてよい。"
        )

    return "\n".join(parts) + "\n"
