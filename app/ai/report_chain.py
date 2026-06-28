from app.ai.llm import llm
from app.ai.report_prompt import REPORT_PROMPT
from app.ai.schemas import ReportAnalysis


class ReportChain:

    def __init__(self):

        self.chain = (
            REPORT_PROMPT
            | llm.with_structured_output(
                ReportAnalysis,
            )
        )

    def invoke(
        self,
        asset_inventory: str,
    ) -> ReportAnalysis:

        return self.chain.invoke(
            {
                "asset_inventory": asset_inventory,
            }
        )


report_chain = ReportChain()