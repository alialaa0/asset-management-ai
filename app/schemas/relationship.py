from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import RelationType


# ==========================================================
# Base Schema
# ==========================================================

class RelationshipBase(BaseModel):
    """
    Common fields shared across relationship schemas.
    """

    source_asset_id: UUID
    target_asset_id: UUID
    relation_type: RelationType


# ==========================================================
# Create Schema
# ==========================================================

class RelationshipCreate(RelationshipBase):
    """
    Schema used when creating a relationship.
    """

    pass


# ==========================================================
# Response Schema
# ==========================================================

class RelationshipResponse(RelationshipBase):
    """
    Schema returned to API clients.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime