"""Module 2 — Trafficking Route Predictor.

Maps known trafficking corridors in India and activates predictive
alerts within 60 seconds of a missing-person report.

Uses NetworkX for graph-based route modelling and provides
deterministic corridor-alert activation for the MVP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import networkx as nx

from backend.config import settings
from backend.models.schemas import (
    AlertPriority,
    RouteCheckpoint,
    TraffickingRoute,
    TransportMode,
)


# ── Known route database (seed data) ─────────────────────────────────

_ROUTE_DB: dict = {
    "sources": [
        "Murshidabad",
        "Malda",
        "North 24 Parganas",
        "South 24 Parganas",
        "Jalpaiguri",
    ],
    "transit_hubs": [
        "Howrah",
        "Sealdah",
        "New Delhi",
        "Mumbai CST",
        "Chennai Central",
    ],
    "destinations": [
        "Delhi",
        "Mumbai",
        "Punjab",
        "Chennai",
    ],
    "edges": [
        ("Murshidabad", "Howrah", {"hours": 5, "mode": "train"}),
        ("Malda", "Howrah", {"hours": 6, "mode": "train"}),
        ("North 24 Parganas", "Sealdah", {"hours": 2, "mode": "bus"}),
        ("South 24 Parganas", "Sealdah", {"hours": 2, "mode": "bus"}),
        ("Jalpaiguri", "Howrah", {"hours": 8, "mode": "train"}),
        ("Howrah", "New Delhi", {"hours": 20, "mode": "train"}),
        ("Howrah", "Mumbai CST", {"hours": 30, "mode": "train"}),
        ("Sealdah", "New Delhi", {"hours": 21, "mode": "train"}),
        ("Sealdah", "Chennai Central", {"hours": 26, "mode": "train"}),
        ("New Delhi", "Delhi", {"hours": 0.5, "mode": "bus"}),
        ("New Delhi", "Punjab", {"hours": 6, "mode": "train"}),
        ("Mumbai CST", "Mumbai", {"hours": 0.5, "mode": "bus"}),
        ("Chennai Central", "Chennai", {"hours": 0.5, "mode": "bus"}),
    ],
}


def _build_graph() -> nx.DiGraph:
    """Build the trafficking corridor graph from seed data."""
    g = nx.DiGraph()
    for src, dst, attrs in _ROUTE_DB["edges"]:
        g.add_edge(src, dst, **attrs)
    return g


_GRAPH: nx.DiGraph = _build_graph()


# ── Public API ────────────────────────────────────────────────────────


@dataclass
class CorridorAlert:
    """Alert dispatched to a single checkpoint along the predicted route."""

    checkpoint: str
    hub_type: str
    estimated_arrival_hours: float
    transport_mode: str
    alert_priority: AlertPriority = AlertPriority.HIGH


@dataclass
class CorridorActivation:
    """Result of activating corridor alerts for a missing person."""

    source: str
    alerts: list[CorridorAlert] = field(default_factory=list)
    routes: list[TraffickingRoute] = field(default_factory=list)


def predict_routes(source: str) -> list[TraffickingRoute]:
    """Return all plausible trafficking routes from *source*.

    Uses shortest-path analysis on the corridor graph to find routes
    from the source to every known destination.
    """
    if source not in _GRAPH:
        return []

    destinations = _ROUTE_DB["destinations"]
    routes: list[TraffickingRoute] = []
    for dest in destinations:
        if dest not in _GRAPH:
            continue
        try:
            path = nx.shortest_path(_GRAPH, source, dest, weight="hours")
        except nx.NetworkXNoPath:
            continue

        checkpoints: list[RouteCheckpoint] = []
        total_hours = 0.0
        modes: list[TransportMode] = []
        for i in range(len(path) - 1):
            edge = _GRAPH.edges[path[i], path[i + 1]]
            total_hours += edge["hours"]
            mode_str = edge.get("mode", "train")
            try:
                mode = TransportMode(mode_str)
            except ValueError:
                mode = TransportMode.TRAIN
            if mode not in modes:
                modes.append(mode)
            checkpoints.append(
                RouteCheckpoint(
                    location=path[i + 1],
                    hub_type="railway_station" if mode == TransportMode.TRAIN else "bus_terminal",
                    estimated_arrival_hours=round(total_hours, 1),
                )
            )

        routes.append(
            TraffickingRoute(
                source=source,
                destination=dest,
                checkpoints=checkpoints,
                transport_modes=modes,
                estimated_total_hours=round(total_hours, 1),
            )
        )
    return routes


def activate_corridor_alerts(
    source: str,
    missing_person_id: Optional[str] = None,
) -> CorridorActivation:
    """Activate alerts along all predicted corridors from *source*.

    This is the core function called within 60 seconds of a missing-
    person report.  It:
    1. Predicts likely routes.
    2. Generates a :class:`CorridorAlert` for each checkpoint.
    """
    routes = predict_routes(source)
    seen: set[str] = set()
    alerts: list[CorridorAlert] = []
    for route in routes:
        for cp in route.checkpoints:
            if cp.location in seen:
                continue
            seen.add(cp.location)
            alerts.append(
                CorridorAlert(
                    checkpoint=cp.location,
                    hub_type=cp.hub_type,
                    estimated_arrival_hours=cp.estimated_arrival_hours or 0,
                    transport_mode=route.transport_modes[0].value if route.transport_modes else "train",
                )
            )
    return CorridorActivation(source=source, alerts=alerts, routes=routes)


def get_known_sources() -> list[str]:
    """Return list of known trafficking source locations."""
    return list(_ROUTE_DB["sources"])


def get_known_destinations() -> list[str]:
    """Return list of known trafficking destination locations."""
    return list(_ROUTE_DB["destinations"])
