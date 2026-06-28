from sqlalchemy.orm import Session

from app.ai.chain import query_chain
from app.schemas.ai import (
    QueryRequest,
    AIQueryResponse,
    AssetResponse,
)
from app.ai.sql_builder import SQLBuilder


class AIService:
    """
    AI service responsible for converting
    natural-language questions into
    grounded database queries.
    """

    def __init__(
        self,
        db: Session,
    ):

        self.db = db

    # ============================================================
    # Natural Language Query
    # ============================================================

    def query_assets(
        self,
        request: QueryRequest,
    ) -> AIQueryResponse:

        # --------------------------------------------------
        # Natural Language → Structured Query
        # --------------------------------------------------

        structured_query = query_chain.invoke(
            request.question,
        )

        # -------------------------------------------------------------
        # Reject out-of-scope questions
        # -------------------------------------------------------------

        question = request.question.lower()

        asset_keywords = [
            "asset",
            "assets",
            "domain",
            "domains",
            "subdomain",
            "subdomains",
            "ip",
            "ip address",
            "service",
            "services",
            "certificate",
            "certificates",
            "technology",
            "technologies",
            "tag",
            "tags",
            "status",
            "source",
            "risk",
            "inventory",
        ]

        if not any(keyword in question for keyword in asset_keywords):
            raise ValueError(
                "Only asset management queries are supported."
            )

        # --------------------------------------------------
        # Structured Query → SQLAlchemy Statement
        # --------------------------------------------------

        statement = SQLBuilder.build(
            structured_query,
        )

        # --------------------------------------------------
        # Execute Query
        # --------------------------------------------------

        assets = self.db.scalars(
            statement,
        ).all()

        # --------------------------------------------------
        # Serialize
        # --------------------------------------------------

        results = [
            AssetResponse(
                id=str(asset.id),
                type=asset.type.value,
                value=asset.value,
                status=asset.status.value,
                source=asset.source,
                tags=asset.tags,
                metadata=asset.metadata_,
                first_seen=asset.first_seen,
                last_seen=asset.last_seen,
            )
            for asset in assets
        ]

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        return AIQueryResponse(
            question=request.question,
            count=len(results),
            results=results,
            structured_query=structured_query,
        )