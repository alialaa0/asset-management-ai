from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.report import (
    ReportRequest,
    ReportResponse,
)

from app.services.report_service import (
    ReportService,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/report",
    response_model=ReportResponse,
    summary="Generate Inventory Report",
)
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
):

    try:

        service = ReportService(
            db,
        )

        return service.generate(
            request,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )