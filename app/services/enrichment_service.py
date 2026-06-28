from sqlalchemy.orm import Session

from app.ai.context_builder import ContextBuilder
from app.ai.enrichment_chain import enrichment_chain
from app.schemas.enrichment import (
    EnrichmentRequest,
    EnrichmentResponse,
)


class EnrichmentService:
    """
    AI-powered asset enrichment service.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

        self.context_builder = ContextBuilder(
            db,
        )

    # ============================================================
    # Public API
    # ============================================================

    def enrich(
        self,
        request: EnrichmentRequest,
    ) -> EnrichmentResponse:

        context = self.context_builder.build(
            request.asset,
        )

        enrichment = enrichment_chain.invoke(
            context,
        )

        return EnrichmentResponse(
            asset=request.asset,
            environment=enrichment.environment,
            category=enrichment.category,
            criticality=enrichment.criticality,
            summary=enrichment.summary,
        )