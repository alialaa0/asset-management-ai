import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RelationType
from app.db.database import Base


class Relationship(Base):
    """
    Represents a relationship between two assets.

    Example:
        Domain ---------> Subdomain
            parent

        Subdomain ------> IP Address
            resolves_to

        Service --------> Technology
            powered_by
    """

    __tablename__ = "relationships"

    __table_args__ = (
        UniqueConstraint(
            "source_asset_id",
            "target_asset_id",
            "relation_type",
            name="uq_relationship",
        ),
        Index("ix_relationship_source", "source_asset_id"),
        Index("ix_relationship_target", "target_asset_id"),
        Index("ix_relationship_type", "relation_type"),
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
    # Foreign Keys
    # ------------------------------------------------------------------

    source_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )

    target_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationship Type
    # ------------------------------------------------------------------

    relation_type: Mapped[RelationType] = mapped_column(
    Enum(
        RelationType,
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
        name="relation_type_enum",
    ),
    nullable=False,
)
    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # ORM Relationships
    # ------------------------------------------------------------------

    source_asset: Mapped["Asset"] = relationship(
        "Asset",
        foreign_keys=[source_asset_id],
        back_populates="outgoing_relationships",
    )

    target_asset: Mapped["Asset"] = relationship(
        "Asset",
        foreign_keys=[target_asset_id],
        back_populates="incoming_relationships",
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<Relationship("
            f"{self.source_asset_id} "
            f"-[{self.relation_type.value}]-> "
            f"{self.target_asset_id}"
            f")>"
        )