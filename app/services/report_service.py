import json

from sqlalchemy.orm import Session

from app.ai.chain import query_chain
from app.ai.report_chain import report_chain
from app.ai.sql_builder import SQLBuilder
from app.schemas.report import (
    ReportRequest,
    ReportResponse,
)


class ReportService:
    """
    Generates grounded inventory reports.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

    # ============================================================
    # Public API
    # ============================================================

    def generate(
        self,
        request: ReportRequest,
    ) -> ReportResponse:

        # --------------------------------------------------------
        # Question -> Structured Query
        # --------------------------------------------------------

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
        # --------------------------------------------------------
        # Structured Query -> SQL
        # --------------------------------------------------------

        statement = SQLBuilder.build(
            structured_query,
        )

        # --------------------------------------------------------
        # Execute SQL
        # --------------------------------------------------------

        assets = self.db.scalars(
            statement,
        ).all()

        # --------------------------------------------------------
        # Serialize Inventory
        # --------------------------------------------------------

        inventory = []

        for asset in assets:

            inventory.append(
                {
                    "type": asset.type.value,
                    "value": asset.value,
                    "status": asset.status.value,
                    "source": asset.source,
                    "tags": asset.tags,
                    "metadata": asset.metadata_,
                }
            )

        # --------------------------------------------------------
        # Build grounded report context
        # --------------------------------------------------------

        report_context = self._build_statistics(
            assets,
        )

        report_context["inventory"] = inventory

        # --------------------------------------------------------
        # Generate report
        # --------------------------------------------------------

        report = report_chain.invoke(
            json.dumps(
                report_context,
                indent=4,
                default=str,
            )
        )

        return ReportResponse(
            question=request.question,
            assets_count=len(inventory),
            report=report.report,
        )

    # ============================================================
    # Helpers
    # ============================================================

    def _build_statistics(
        self,
        assets,
    ) -> dict:

        stats = {
            "total_assets": len(assets),
            "domains": 0,
            "subdomains": 0,
            "ip_addresses": 0,
            "services": 0,
            "technologies": 0,
            "certificates": 0,
            "active": 0,
            "stale": 0,
            "archived": 0,
        }

        facts = []

        for asset in assets:

            asset_type = asset.type.value
            asset_status = asset.status.value

            if asset_type == "domain":
                stats["domains"] += 1

            elif asset_type == "subdomain":
                stats["subdomains"] += 1

            elif asset_type == "ip_address":
                stats["ip_addresses"] += 1

            elif asset_type == "service":
                stats["services"] += 1

            elif asset_type == "technology":
                stats["technologies"] += 1

            elif asset_type == "certificate":
                stats["certificates"] += 1

            if asset_status == "active":
                stats["active"] += 1

            elif asset_status == "stale":
                stats["stale"] += 1

            elif asset_status == "archived":
                stats["archived"] += 1

            if "production" in asset.tags:
                facts.append(
                    f"{asset.value} is tagged as production."
                )

            if "critical" in asset.tags:
                facts.append(
                    f"{asset.value} is tagged as critical."
                )

        if stats["certificates"] == 0:
            facts.append(
                "No certificate assets are present."
            )

        return {
            "statistics": stats,
            "facts": facts,
        }