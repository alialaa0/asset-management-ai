from sqlalchemy import Select, select

from app.ai.schemas import AssetQuery
from app.models.asset import Asset


class SQLBuilder:
    """
    Converts an AssetQuery object into
    a SQLAlchemy Select statement.
    """

    @staticmethod
    def build(
        query: AssetQuery,
    ) -> Select:

        stmt = select(Asset)

        filters = query.filters

        # --------------------------------------------------
        # Asset Type
        # --------------------------------------------------

        if filters.type is not None:
            stmt = stmt.where(
                Asset.type == filters.type,
            )

        # --------------------------------------------------
        # Status
        # --------------------------------------------------

        if filters.status is not None:
            stmt = stmt.where(
                Asset.status == filters.status,
            )

        # --------------------------------------------------
        # Source
        # --------------------------------------------------

        if filters.source is not None:
            stmt = stmt.where(
                Asset.source == filters.source,
            )

        # --------------------------------------------------
        # Value Search
        # --------------------------------------------------

        if filters.value_contains is not None:
            stmt = stmt.where(
                Asset.value.ilike(
                    f"%{filters.value_contains}%"
                )
            )

        # --------------------------------------------------
        # Tags
        # --------------------------------------------------

        if filters.tag is not None:
            stmt = stmt.where(
                Asset.tags.any(
                    filters.tag
                )
            )

        # --------------------------------------------------
        # Sorting
        # --------------------------------------------------

        sort_column = getattr(
            Asset,
            query.sort.field,
        )

        if query.sort.order == "desc":

            stmt = stmt.order_by(
                sort_column.desc()
            )

        else:

            stmt = stmt.order_by(
                sort_column.asc()
            )

        # --------------------------------------------------
        # Limit
        # --------------------------------------------------

        stmt = stmt.limit(
            query.limit
        )

        return stmt