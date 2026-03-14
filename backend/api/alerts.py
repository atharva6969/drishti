"""API endpoints for alert management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.modules.transport_hub import (
    HubType,
    TransportHub,
    TransportHubRegistry,
)

router = APIRouter()

_registry = TransportHubRegistry()


@router.post("/hub", status_code=201)
def register_hub(
    hub_id: str,
    name: str,
    hub_type: HubType,
    state: str,
    latitude: float,
    longitude: float,
    camera_count: int = 0,
) -> dict:
    hub = TransportHub(
        hub_id=hub_id,
        name=name,
        hub_type=hub_type,
        state=state,
        latitude=latitude,
        longitude=longitude,
        camera_count=camera_count,
    )
    _registry.register_hub(hub)
    return {"hub_id": hub_id, "status": "registered"}


@router.post("/hub/{hub_id}/alert")
def trigger_hub_alert(
    hub_id: str,
    missing_person_id: str,
    confidence: float,
) -> dict:
    record = _registry.execute_alert_protocol(hub_id, missing_person_id, confidence)
    if record is None:
        raise HTTPException(status_code=404, detail="Hub not found or inactive")
    return {
        "hub_id": hub_id,
        "steps_completed": [s.value for s in record.steps_completed],
        "verified": record.verified,
    }


@router.get("/hub")
def list_hubs(hub_type: HubType | None = None, state: str | None = None) -> list[dict]:
    hubs = _registry.list_hubs(hub_type=hub_type, state=state)
    return [{"hub_id": h.hub_id, "name": h.name, "type": h.hub_type.value} for h in hubs]
