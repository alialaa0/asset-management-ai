from pathlib import Path
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.import_service import ImportService

router = APIRouter(
    prefix="/import",
    tags=["Import"],
)


@router.post("/")
async def import_assets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Import a JSON dataset into the asset inventory.
    """

    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are supported.",
        )

    try:

        contents = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".json",
        ) as temp_file:

            temp_file.write(contents)

            temp_path = Path(temp_file.name)

        service = ImportService(db)

        result = service.execute(
            temp_path,
        )

        temp_path.unlink(
            missing_ok=True,
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:

        # raise

        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        )