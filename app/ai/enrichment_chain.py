from app.ai.enrichment_prompt import ENRICHMENT_PROMPT
from app.ai.llm import llm
from app.ai.schemas import AssetEnrichment


class EnrichmentChain:

    def __init__(self):

        self.chain = (
            ENRICHMENT_PROMPT
            | llm.with_structured_output(
                AssetEnrichment,
            )
        )

    def invoke(
        self,
        asset_data: str,
    ) -> AssetEnrichment:

        return self.chain.invoke(
            {
                "asset_data": asset_data,
            }
        )


enrichment_chain = EnrichmentChain()