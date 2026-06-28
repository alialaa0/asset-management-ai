from pydantic import BaseModel


class ReportRequest(BaseModel):
    """
    Natural-language report request.
    """

    question: str


class ReportResponse(BaseModel):
    """
    AI generated report.
    """

    question: str

    assets_count: int

    report: str