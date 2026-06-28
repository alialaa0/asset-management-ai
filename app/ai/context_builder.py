import json

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.asset import Asset
from app.models.relationship import Relationship


class ContextBuilder:
    """
    Builds a grounded context for an asset.

    The context is retrieved from PostgreSQL
    and provided to the LLM so that every
    analysis is grounded in real data.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

    # ============================================================
    # Public API
    # ============================================================

    def build(
        self,
        asset_value: str,
    ) -> str:
        """
        Build a JSON context for an asset value.
        """

        asset = (
            self.db.execute(
                select(Asset)
                .options(
                    selectinload(
                        Asset.outgoing_relationships,
                    ).selectinload(
                        Relationship.target_asset,
                    ),
                    selectinload(
                        Asset.incoming_relationships,
                    ).selectinload(
                        Relationship.source_asset,
                    ),
                )
                .where(
                    Asset.value == asset_value,
                )
            )
            .scalars()
            .first()
        )

        if asset is None:

            raise ValueError(
                f"Asset '{asset_value}' not found."
            )

        
        context = {
           "asset": self._serialize_asset(asset),
           "allowed_tags": asset.tags,
           "outgoing_relationships": self._serialize_relationships(
              asset.outgoing_relationships,
              outgoing=True,
            ),

           "incoming_relationships": self._serialize_relationships(
            asset.incoming_relationships,
            outgoing=False,
          ),
        }

        return json.dumps(
            context,
            indent=4,
            default=str,
        )

    # ============================================================
    # Asset
    # ============================================================

    @staticmethod
    def _serialize_asset(
        asset: Asset,
    ) -> dict:

        return {
            "id": str(asset.id),
            "type": asset.type.value,
            "value": asset.value,
            "status": asset.status.value,
            "source": asset.source,
            "tags": asset.tags,
            "metadata": asset.metadata_,
            "first_seen": asset.first_seen,
            "last_seen": asset.last_seen,
        }

    # ============================================================
    # Relationships
    # ============================================================

    @staticmethod
    def _serialize_relationships(
        relationships,
        *,
        outgoing: bool,
    ) -> list[dict]:

        result = []

        for relation in relationships:

            other = (
                relation.target_asset
                if outgoing
                else relation.source_asset
            )

            result.append(
                {
                    "relation_type": relation.relation_type.value,
                    "asset": {
                        "id": str(other.id),
                        "type": other.type.value,
                        "value": other.value,
                        "status": other.status.value,
                    },
                }
            )

        return result