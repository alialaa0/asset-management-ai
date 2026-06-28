from fastapi import FastAPI


from app.api.import_router import router as import_router

from app.api.ai_router import (
    router as ai_router,
)

from app.api.risk_router import (
    router as risk_router,
)
from app.api.enrichment_router import (
    router as enrichment_router,
)

from app.api.report_router import (
    router as report_router,
)



app = FastAPI(
    title="Asset Management AI",
    description="DarkAtlas Asset Management API",
    version="1.0.0",
)

app.include_router(import_router)


@app.get("/")
def root():
    return {
        "message": "Asset Management AI API is running.",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }

app.include_router(
    ai_router,
)

app.include_router(
    risk_router,
)

app.include_router(
    enrichment_router,
)

app.include_router(
    report_router,
)