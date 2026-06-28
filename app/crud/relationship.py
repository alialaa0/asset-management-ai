from sqlalchemy.orm import Session

from app.core.enums import RelationType
from app.models.relationship import Relationship


# ==========================================================
# Queries
# ==========================================================

def get_relationship(
    db: Session,
    source_asset_id,
    target_asset_id,
    relation_type: RelationType,
) -> Relationship | None:
    """
    Return a relationship if it already exists.
    """

    return (
        db.query(Relationship)
        .filter(
            Relationship.source_asset_id == source_asset_id,
            Relationship.target_asset_id == target_asset_id,
            Relationship.relation_type == relation_type,
        )
        .first()
    )


def get_relationships_for_asset(
    db: Session,
    asset_id,
) -> list[Relationship]:
    """
    Return all relationships where the asset is either
    the source or the target.
    """

    return (
        db.query(Relationship)
        .filter(
            (Relationship.source_asset_id == asset_id)
            | (Relationship.target_asset_id == asset_id)
        )
        .all()
    )


# ==========================================================
# Commands
# ==========================================================

def create_relationship(
    db: Session,
    relationship: Relationship,
) -> Relationship:
    """
    Persist a new relationship.
    """

    db.add(relationship)
    db.flush()

    return relationship


def delete_relationship(
    db: Session,
    relationship: Relationship,
) -> None:
    """
    Delete an existing relationship.
    """

    db.delete(relationship)
    db.flush()