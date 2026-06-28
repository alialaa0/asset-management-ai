from app.ai.llm import llm
from app.ai.risk_prompts import RISK_PROMPT
from app.ai.schemas import RiskAnalysis


class RiskChain:
    """
    Generates a grounded risk assessment
    using only the provided asset context.
    """

    def __init__(self) -> None:

        self.chain = (
            RISK_PROMPT
            | llm.with_structured_output(
                RiskAnalysis,
            )
        )

    def invoke(
        self,
        asset_data: str,
    ) -> RiskAnalysis:

        return self.chain.invoke(
            {
                "asset_data": asset_data,
            }
        )


risk_chain = RiskChain()