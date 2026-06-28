from app.ai.llm import llm
from app.ai.prompts import QUERY_PROMPT
from app.ai.schemas import (
    AssetQuery,
)


class QueryChain:
    """
    Converts a natural-language question
    into a validated AssetQuery object.
    """

    def __init__(self):

        self.chain = (
            QUERY_PROMPT
            | llm.with_structured_output(
                AssetQuery
            )
        )

    def invoke(
        self,
        question: str,
    ) -> AssetQuery:

        return self.chain.invoke(
            {
                "question": question,
            }
        )


query_chain = QueryChain()