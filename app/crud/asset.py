from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import AssetType
from app.models.asset import Asset


# ==========================================================
# Queries
# ==========================================================

def get_asset_by_id(
    db: Session,
    asset_id: UUID,
) -> Asset | None:
    """
    Return an asset by its UUID.
    """

    return (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )


def get_asset_by_external_id(
    db: Session,
    external_id: str,
) -> Asset | None:
    """
    Return an asset using the imported dataset ID.
    """

    return (
        db.query(Asset)
        .filter(Asset.external_id == external_id)
        .first()
    )


def get_asset_by_type_value(
    db: Session,
    asset_type: AssetType,
    value: str,
) -> Asset | None:
    """
    Used for deduplication.
    """

    return (
        db.query(Asset)
        .filter(
            Asset.type == asset_type,
            Asset.value == value,
        )
        .first()
    )


def get_all_assets(
    db: Session,
) -> list[Asset]:
    """
    Return all assets.
    """

    return (
        db.query(Asset)
        .all()
    )


# ==========================================================
# Commands
# ==========================================================

def create_asset(
    db: Session,
    asset: Asset,
) -> Asset:
    """
    Persist a new asset.
    """

    db.add(asset)
    db.flush()

    return asset


def update_asset(
    db: Session,
    asset: Asset,
) -> Asset:
    """
    Flush pending changes.
    """

    db.flush()

    return asset


def delete_asset(
    db: Session,
    asset: Asset,
) -> None:
    """
    Delete an asset.
    """

    db.delete(asset)
    db.flush()


# ==========================================================
# Search Helpers
# ==========================================================

def search_assets(
    db: Session,
    *,
    asset_type: AssetType | None = None,
    status=None,
    value_contains: str | None = None,
):
    """
    Base query used by the API.
    """

    query = db.query(Asset)

    if asset_type is not None:
        query = query.filter(
            Asset.type == asset_type,
        )

    if status is not None:
        query = query.filter(
            Asset.status == status,
        )

    if value_contains:

        query = query.filter(
            Asset.value.ilike(
                f"%{value_contains}%"
            )
        )

    return query