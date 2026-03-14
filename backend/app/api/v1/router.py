"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, cases, sightings, alerts, search, community

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(cases.router, prefix="/cases", tags=["missing persons"])
api_router.include_router(sightings.router, prefix="/sightings", tags=["sightings"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(search.router, prefix="/search", tags=["AI search"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
