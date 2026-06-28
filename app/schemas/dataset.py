from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AssetStatus, AssetType


class ImportedAsset(BaseModel):
    """
    Represents a single asset exactly as it appears
    in the imported JSON dataset.
    """

    model_config = ConfigDict(
        extra="allow",
    )

    id: str = Field(
        ...,
        description="External identifier from the dataset.",
    )

    type: AssetType

    value: str

    status: AssetStatus

    source: str

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    # Optional relationship fields
    parent: str | None = None

    covers: str | None = None