"""API endpoints for community sightings."""

from __future__ import annotations

from fastapi import APIRouter

from backend.models.schemas import Sighting
from backend.modules.community_network import CommunityNetwork

router = APIRouter()

_community = CommunityNetwork()


@router.post("/", status_code=201)
def submit_sighting(sighting: Sighting) -> dict:
    saved = _community.submit_sighting(sighting)
    return {"id": saved.id, "status": "recorded"}


@router.get("/")
def list_sightings(missing_person_id: str | None = None) -> list[dict]:
    sightings = _community.get_sightings(missing_person_id)
    return [
        {
            "id": s.id,
            "location": s.location,
            "timestamp": s.timestamp.isoformat(),
            "missing_person_id": s.missing_person_id,
        }
        for s in sightings
    ]
