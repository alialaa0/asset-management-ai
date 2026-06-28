from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session
from app.schemas.ai import (
    QueryRequest,
    AIQueryResponse,
)
from app.db.database import get_db

from app.services.ai_service import AIService


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# ============================================================
# Natural Language Query
# ============================================================

@router.post(
    "/query",
    response_model=AIQueryResponse,
    summary="Natural Language Asset Query",
)
async def query_assets(
    request: QueryRequest,
    db: Session = Depends(get_db),
) -> AIQueryResponse:

    try:

        service = AIService(
            db,
        )

        return service.query_assets(
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