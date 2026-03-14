"""API endpoints for trafficking-route prediction."""

from __future__ import annotations

from fastapi import APIRouter

from backend.modules.route_predictor import (
    activate_corridor_alerts,
    get_known_destinations,
    get_known_sources,
    predict_routes,
)

router = APIRouter()


@router.get("/sources")
def list_sources() -> list[str]:
    return get_known_sources()


@router.get("/destinations")
def list_destinations() -> list[str]:
    return get_known_destinations()


@router.get("/predict/{source}")
def predict(source: str) -> list[dict]:
    routes = predict_routes(source)
    return [
        {
            "id": r.id,
            "source": r.source,
            "destination": r.destination,
            "checkpoints": [
                {"location": cp.location, "hours": cp.estimated_arrival_hours}
                for cp in r.checkpoints
            ],
            "total_hours": r.estimated_total_hours,
        }
        for r in routes
    ]


@router.post("/activate/{source}")
def activate(source: str) -> dict:
    activation = activate_corridor_alerts(source)
    return {
        "source": activation.source,
        "alerts_count": len(activation.alerts),
        "routes_count": len(activation.routes),
        "checkpoints": [a.checkpoint for a in activation.alerts],
    }
