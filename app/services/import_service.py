from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.enums import (
    AssetStatus,
    RelationType,
)
from app.crud.asset import (
    create_asset,
    get_asset_by_type_value,
    update_asset,
)
from app.crud.relationship import (
    create_relationship,
    get_relationship,
)
from app.models.asset import Asset
from app.models.relationship import Relationship
from app.schemas.dataset import ImportedAsset
from app.utils.json_loader import load_json_file


class ImportService:
    """
    Handles importing DarkAtlas datasets.

    Responsibilities
    ----------------
    - Read JSON
    - Validate records
    - Deduplicate assets
    - Merge metadata
    - Merge tags
    - Reactivate stale assets
    - Create relationships
    - Return import statistics
    """

    RELATION_FIELDS = {
        "parent": RelationType.PARENT,
        "covers": RelationType.COVERS,
    }

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        # dataset id  -> database asset
        self.asset_mapping: dict[str, Asset] = {}

    # =====================================================
    # Public API
    # =====================================================

    def import_file(
        self,
        file_path: str | Path,
    ) -> dict:
        """
        Import a JSON dataset.
        """

        raw_records = load_json_file(file_path)

        valid_assets: list[ImportedAsset] = []
        failed_records = []

        for index, record in enumerate(raw_records):

            try:

                asset = ImportedAsset.model_validate(
                    record,
                )

                valid_assets.append(asset)

            except ValidationError as exc:

                failed_records.append(
                    {
                        "row": index,
                        "error": str(exc),
                        "record": record,
                    }
                )

        # ----------------------------------------
        # Import assets
        # ----------------------------------------

        created, updated = self._import_assets(
            valid_assets,
        )

        # ----------------------------------------
        # Import relationships
        # ----------------------------------------

        relationships = self._import_relationships(
            valid_assets,
        )

        summary = self.build_summary(
            total_records=len(raw_records),
            valid_records=len(valid_assets),
            failed_records=len(failed_records),
            assets_created=created,
            assets_updated=updated,
            relationships_created=relationships,
        )

        self.log_summary(summary)

        summary["errors"] = failed_records

        return summary

    # =====================================================
    # Asset Import
    # =====================================================

    def _import_assets(
        self,
        assets: list[ImportedAsset],
    ) -> tuple[int, int]:

        created = 0
        updated = 0

        for asset in assets:

            existing = get_asset_by_type_value(
                self.db,
                asset.type,
                asset.value,
            )

            if existing:

                self._merge_asset(
                    existing,
                    asset,
                )

                self.asset_mapping[
                    asset.id
                ] = existing

                updated += 1

                continue

            db_asset = Asset(
                external_id=asset.id,
                type=asset.type,
                value=asset.value,
                status=asset.status,
                source=asset.source,
                tags=asset.tags,
                metadata_=asset.metadata,
            )

            create_asset(
                self.db,
                db_asset,
            )

            self.asset_mapping[
                asset.id
            ] = db_asset

            created += 1

        return created, updated
    

    # =====================================================
    # Merge Existing Asset
    # =====================================================

    def _merge_asset(
        self,
        existing: Asset,
        incoming: ImportedAsset,
    ) -> None:
        """
        Merge an imported asset into an existing database asset.
        """

        # -----------------------------
        # Lifecycle
        # -----------------------------

        if existing.status == AssetStatus.STALE:
            existing.status = AssetStatus.ACTIVE

        # -----------------------------
        # Source
        # -----------------------------

        existing.source = incoming.source

        # -----------------------------
        # Last Seen
        # -----------------------------

        existing.last_seen = datetime.utcnow()

        # -----------------------------
        # Tags
        # -----------------------------

        existing.tags = self.merge_tags(
           existing.tags,
           incoming.tags,
              )

        # -----------------------------
        # Metadata
        # -----------------------------

        merged_metadata = dict(existing.metadata_)

        merged_metadata.update(
            incoming.metadata
        )

        existing.metadata_ = merged_metadata

        # -----------------------------
        # External ID
        # -----------------------------

        if existing.external_id is None:
            existing.external_id = incoming.id

        update_asset(
            self.db,
            existing,
        )

    # =====================================================
    # Relationship Import
    # =====================================================

    def _import_relationships(
        self,
        assets: list[ImportedAsset],
    ) -> int:
        """
        Create graph relationships after all assets
        have been imported.
        """

        created = 0

        for asset in assets:

            source_asset = self.asset_mapping.get(
                asset.id,
            )

            if source_asset is None:
                continue

            for field_name, relation_type in self.RELATION_FIELDS.items():

                related_external_id = getattr(
                    asset,
                    field_name,
                    None,
                )

                if not related_external_id:
                    continue

                target_asset = self.asset_mapping.get(
                    related_external_id,
                )

                if target_asset is None:
                    continue

                existing = get_relationship(
                    self.db,
                    source_asset.id,
                    target_asset.id,
                    relation_type,
                )

                if existing:
                    continue

                relationship = Relationship(
                    source_asset_id=source_asset.id,
                    target_asset_id=target_asset.id,
                    relation_type=relation_type,
                )

                create_relationship(
                    self.db,
                    relationship,
                )

                created += 1

        return created
    

    # =====================================================
    # Validation Helpers
    # =====================================================

    def validate_dataset(
        self,
        file_path: str | Path,
    ) -> list[ImportedAsset]:
        """
        Validate a dataset without importing it.
        """

        raw_records = load_json_file(file_path)

        validated = []

        for index, record in enumerate(raw_records):

            try:

                validated.append(
                    ImportedAsset.model_validate(record)
                )

            except ValidationError as exc:

                raise ValueError(
                    f"Invalid record at index {index}: {exc}"
                ) from exc

        return validated

    # =====================================================
    # Preview
    # =====================================================

    def preview_import(
        self,
        file_path: str | Path,
    ) -> dict:
        """
        Preview dataset statistics before import.
        """

        assets = self.validate_dataset(
            file_path,
        )

        relationship_count = 0

        asset_types: dict[str, int] = {}

        for asset in assets:

            asset_types.setdefault(
                asset.type.value,
                0,
            )

            asset_types[
                asset.type.value
            ] += 1

            for field in self.RELATION_FIELDS:

                if getattr(asset, field):

                    relationship_count += 1

        return {
            "total_assets": len(assets),
            "relationship_count": relationship_count,
            "asset_types": asset_types,
        }

    # =====================================================
    # Statistics
    # =====================================================

    @staticmethod
    def build_summary(
        *,
        total_records: int,
        valid_records: int,
        failed_records: int,
        assets_created: int,
        assets_updated: int,
        relationships_created: int,
    ) -> dict:

        return {
            "total_records": total_records,
            "valid_records": valid_records,
            "failed_records": failed_records,
            "assets_created": assets_created,
            "assets_updated": assets_updated,
            "relationships_created": relationships_created,
        }
        # =====================================================
    # Transaction Helpers
    # =====================================================

    def safe_import(
        self,
        file_path: str | Path,
    ) -> dict:
        """
        Import a dataset inside a database transaction.
        Automatically rolls back on failure.
        """

        try:

            result = self.import_file(
                file_path,
            )

            self.db.commit()

            return result

        except Exception:

            self.db.rollback()

            raise

    # =====================================================
    # Lookup Helpers
    # =====================================================

    def get_asset_from_mapping(
        self,
        external_id: str,
    ) -> Asset | None:
        """
        Return an asset from the in-memory mapping.
        """

        return self.asset_mapping.get(
            external_id,
        )

    def has_asset(
        self,
        external_id: str,
    ) -> bool:
        """
        Check whether an imported asset exists
        inside the current import mapping.
        """

        return external_id in self.asset_mapping

    # =====================================================
    # Internal Utilities
    # =====================================================

    @staticmethod
    def merge_tags(
        current: list[str],
        incoming: list[str],
    ) -> list[str]:
        """
        Merge tags while removing duplicates.
        """

        return sorted(
            set(current).union(incoming)
        )

    @staticmethod
    def merge_metadata(
        current: dict,
        incoming: dict,
    ) -> dict:
        """
        Merge metadata dictionaries.

        Incoming values overwrite existing values.
        """

        merged = dict(current)

        merged.update(
            incoming,
        )

        return merged

    @staticmethod
    def reactivate_asset(
        asset: Asset,
    ) -> None:
        """
        Reactivate stale assets when rediscovered.
        """

        if asset.status == AssetStatus.STALE:

            asset.status = AssetStatus.ACTIVE

    @staticmethod
    def touch_asset(
        asset: Asset,
    ) -> None:
        """
        Update discovery timestamp.
        """

        asset.last_seen = datetime.utcnow()

        # =====================================================
    # Logging Helpers
    # =====================================================

    @staticmethod
    def log_summary(summary: dict) -> None:
        """
        Print a simple import summary.
        Replace with a proper logger later.
        """

        print("=" * 60)
        print("Import Summary")
        print("=" * 60)

        for key, value in summary.items():
            print(f"{key}: {value}")

        print("=" * 60)

    # =====================================================
    # Reset State
    # =====================================================

    def reset(self) -> None:
        """
        Clear in-memory state after import.
        """

        self.asset_mapping.clear()

    # =====================================================
    # Context Manager
    # =====================================================

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):
        """
        Roll back any pending transaction
        if an unexpected exception occurs.
        """

        if exc_type is not None:
            self.db.rollback()

        self.reset()

    # =====================================================
    # Health Check
    # =====================================================

    def health(self) -> dict:
        """
        Small helper used by tests.
        """

        return {
            "database_connected": self.db.is_active,
            "cached_assets": len(self.asset_mapping),
        }


    # =====================================================
    # Final Cleanup
    # =====================================================

    def close(self) -> None:
        """
        Clear temporary state after import.
        """

        self.reset()

    # =====================================================
    # Safe Execution
    # =====================================================

    def execute(
        self,
        file_path: str | Path,
    ) -> dict:
        """
        Execute the complete import inside
        a database transaction.
        """

        try:

            result = self.import_file(
                file_path,
            )

            self.db.commit()

            return result

        except Exception:

            self.db.rollback()

            raise

        finally:

            self.reset()

    # =====================================================
    # Utility
    # =====================================================

    @property
    def cached_assets(self) -> int:
        """
        Number of cached assets during import.
        """

        return len(self.asset_mapping)

    def __repr__(self) -> str:
        return (
            f"ImportService("
            f"cached_assets={self.cached_assets}"
            f")"
        )




