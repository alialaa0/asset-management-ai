from app.ai.llm import llm
from app.ai.prompts import INTENT_PROMPT
from app.ai.schemas import IntentResponse


class IntentChain:
    """
    Detects the user's intent from
    a natural-language request.
    """

    def __init__(self) -> None:

        self.chain = (
            INTENT_PROMPT
            | llm.with_structured_output(
                IntentResponse,
            )
        )

    def invoke(
        self,
        question: str,
    ) -> IntentResponse:

        return self.chain.invoke(
            {
                "question": question,
            }
        )


intent_chain = IntentChain()