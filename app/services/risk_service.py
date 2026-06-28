from app.ai.context_builder import ContextBuilder
from app.ai.risk_chain import risk_chain
from app.schemas.risk import (
    RiskRequest,
    RiskResponse,
)

from sqlalchemy.orm import Session


class RiskService:
    """
    Service responsible for generating
    grounded risk assessments.
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

    def analyze(
        self,
        request: RiskRequest,
    ) -> RiskResponse:
        """
        Analyze a single asset.
        """

        # --------------------------------------------------
        # Build grounded context
        # --------------------------------------------------

        context = self.context_builder.build(
            request.asset,
        )

        # --------------------------------------------------
        # AI Analysis
        # --------------------------------------------------

        analysis = risk_chain.invoke(
            context,
        )

        # --------------------------------------------------
        # API Response
        # --------------------------------------------------

        return RiskResponse(
            asset=request.asset,
            risk_level=analysis.risk_level,
            summary=analysis.summary,
            findings=analysis.findings,
            recommendations=analysis.recommendations,
        )