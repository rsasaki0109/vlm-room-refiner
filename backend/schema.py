"""部屋分析結果のPydanticスキーマ。Ollamaの structured output 用に JSON Schema を生成する。"""

from pydantic import BaseModel, ConfigDict, Field

MAX_ITEMS = 5


def room_analysis_json_schema() -> dict:
    """Ollama `format` に渡す JSON Schema（Pydantic v2）。"""
    return RoomAnalysis.model_json_schema()


class RoomAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_type: str = Field(
        ..., description="推定する部屋タイプ（例：ワンルーム、リビング＋ダイニング、寝室）"
    )
    style: str = Field(
        ...,
        description="推定するインテリアスタイル（例：北欧、無印系ミニマル、木質ナチュラル）",
    )
    problems: list[str] = Field(
        ...,
        description="改善が必要な点。具体的に、箇条書きレベルで短く",
        min_length=1,
        max_length=MAX_ITEMS,
    )
    recommendations: list[str] = Field(
        ...,
        description="すぐ取り組める改善提案。具体的に、優先度の高い順",
        min_length=1,
        max_length=MAX_ITEMS,
    )
    shopping_keywords: list[str] = Field(
        ...,
        description="家具・小物の購入候補として使える検索キーワード（例：円形ラグ 160cm、間接照明 床置き）",
        min_length=1,
        max_length=MAX_ITEMS,
    )
