from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.risk import (
    RiskRequest,
    RiskResponse,
)
from app.services.risk_service import RiskService


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/risk",
    response_model=RiskResponse,
    summary="Grounded Risk Analysis",
)
async def analyze_asset(
    request: RiskRequest,
    db: Session = Depends(get_db),
) -> RiskResponse:

    try:

        service = RiskService(
            db,
        )

        return service.analyze(
            request,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        )