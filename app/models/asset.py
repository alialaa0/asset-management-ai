import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Enum,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AssetStatus, AssetType
from app.db.database import Base


class Asset(Base):
    """
    Represents any asset discovered within the attack surface.
    """

    __tablename__ = "assets"

    __table_args__ = (
        UniqueConstraint(
            "type",
            "value",
            name="uq_asset_type_value",
        ),
        Index("ix_asset_value", "value"),
    
    )

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ------------------------------------------------------------------
    # External Dataset ID
    # ------------------------------------------------------------------

    external_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Asset Information
    # ------------------------------------------------------------------

    type: Mapped[AssetType] = mapped_column(
        Enum(
            AssetType,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            name="asset_type_enum",
        ),
        nullable=False,
    )

    value: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    status: Mapped[AssetStatus] = mapped_column(
        Enum(
            AssetStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            name="asset_status_enum",
        ),
        default=AssetStatus.ACTIVE,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    # ------------------------------------------------------------------
    # Discovery Tracking
    # ------------------------------------------------------------------

    first_seen: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    last_seen: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Flexible Data
    # ------------------------------------------------------------------

    tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        nullable=False,
    )

    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    outgoing_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.source_asset_id",
        back_populates="source_asset",
        cascade="all, delete-orphan",
    )

    incoming_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.target_asset_id",
        back_populates="target_asset",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<Asset("
            f"id={self.id}, "
            f"type={self.type.value}, "
            f"value='{self.value}'"
            f")>"
        )