"""FastAPI application — DRISHTI backend entry-point."""

from __future__ import annotations

from fastapi import FastAPI

from backend.api.missing_persons import router as missing_persons_router
from backend.api.alerts import router as alerts_router
from backend.api.sightings import router as sightings_router
from backend.api.routes import router as routes_router
from backend.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

app.include_router(missing_persons_router, prefix="/api/v1/persons", tags=["Missing Persons"])
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(sightings_router, prefix="/api/v1/sightings", tags=["Sightings"])
app.include_router(routes_router, prefix="/api/v1/routes", tags=["Routes"])


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "system": settings.APP_NAME, "version": settings.APP_VERSION}
