from pydantic import BaseModel


class EnrichmentRequest(BaseModel):
    """
    Request for AI asset enrichment.
    """

    asset: str


class EnrichmentResponse(BaseModel):
    """
    AI enrichment response.
    """

    asset: str

    environment: str

    category: str

    criticality: str

    summary: str