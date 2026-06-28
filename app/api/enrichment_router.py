from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.enrichment import (
    EnrichmentRequest,
    EnrichmentResponse,
)

from app.services.enrichment_service import (
    EnrichmentService,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/enrich",
    response_model=EnrichmentResponse,
    summary="AI Asset Enrichment",
)
async def enrich_asset(
    request: EnrichmentRequest,
    db: Session = Depends(get_db),
):

    try:

        service = EnrichmentService(
            db,
        )

        return service.enrich(
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