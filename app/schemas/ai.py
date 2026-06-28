from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.ai.schemas import AssetQuery


# ============================================================
# Requests
# ============================================================

class QueryRequest(BaseModel):
    """
    Natural-language query sent by the user.
    """

    question: str = Field(
        ...,
        min_length=3,
        description="Natural language asset query.",
    )


# ============================================================
# Responses
# ============================================================

class AssetResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    type: str

    value: str

    status: str

    source: str

    tags: list[str]

    metadata: dict[str, Any]

    first_seen: datetime

    last_seen: datetime


class AIQueryResponse(BaseModel):

    question: str

    count: int

    results: list[AssetResponse]

    structured_query: AssetQuery | None = None