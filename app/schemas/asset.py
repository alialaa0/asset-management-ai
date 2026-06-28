from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AssetStatus, AssetType


# ==========================================================
# Base Schema
# ==========================================================

class AssetBase(BaseModel):
    """
    Common fields shared across asset schemas.
    """

    type: AssetType
    value: str = Field(..., min_length=1, max_length=512)

    status: AssetStatus = AssetStatus.ACTIVE

    source: str = Field(..., min_length=1, max_length=100)

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


# ==========================================================
# Create Schema
# ==========================================================

class AssetCreate(AssetBase):
    """
    Schema used when creating a new asset.
    """

    external_id: str | None = None


# ==========================================================
# Update Schema
# ==========================================================

class AssetUpdate(BaseModel):
    """
    Schema used for partial updates.
    """

    type: AssetType | None = None
    value: str | None = Field(default=None, max_length=512)

    status: AssetStatus | None = None

    source: str | None = Field(default=None, max_length=100)

    tags: list[str] | None = None

    metadata: dict[str, Any] | None = None


# ==========================================================
# Response Schema
# ==========================================================

class AssetResponse(AssetBase):
    """
    Schema returned to API clients.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    external_id: str | None

    first_seen: datetime
    last_seen: datetime

    created_at: datetime
    updated_at: datetime