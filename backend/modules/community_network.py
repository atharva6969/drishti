"""Module 3 — Community Intelligence Network.

Turns every phone into a sighting node.  Within minutes of a missing-
person report the system can push alerts to verified community
reporters within a configurable radius and collect sighting reports
back into the intelligence pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from backend.config import settings
from backend.models.schemas import AlertPriority, MissingPerson, Sighting


# ── Community reporter registry (in-memory for MVP) ──────────────────


@dataclass
class CommunityReporter:
    """A verified community reporter node."""

    phone: str
    name: str
    latitude: float
    longitude: float
    active: bool = True


class CommunityNetwork:
    """Manages the community alert fan-out and sighting collection."""

    def __init__(self) -> None:
        self._reporters: list[CommunityReporter] = []
        self._sightings: list[Sighting] = []
        self._dispatched_alerts: list[dict] = []

    # ── Reporter management ───────────────────────────────────────

    def register_reporter(self, reporter: CommunityReporter) -> None:
        self._reporters.append(reporter)

    def get_reporters_in_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = settings.COMMUNITY_ALERT_RADIUS_KM,
    ) -> list[CommunityReporter]:
        """Return active reporters within *radius_km* of a point.

        Uses a simplified Euclidean approximation (1 deg ≈ 111 km).
        A production system would use Haversine or PostGIS.
        """
        km_per_deg = 111.0
        results: list[CommunityReporter] = []
        for r in self._reporters:
            if not r.active:
                continue
            dlat = abs(r.latitude - latitude) * km_per_deg
            dlon = abs(r.longitude - longitude) * km_per_deg
            dist = (dlat**2 + dlon**2) ** 0.5
            if dist <= radius_km:
                results.append(r)
        return results[: settings.COMMUNITY_ALERT_MAX_RECIPIENTS]

    # ── Alert dispatch ────────────────────────────────────────────

    def dispatch_alert(
        self,
        person: MissingPerson,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None,
    ) -> list[dict]:
        """Send alert to nearby community reporters.

        Returns a list of dispatch records (phone, message, timestamp).
        """
        if radius_km is None:
            radius_km = settings.COMMUNITY_ALERT_RADIUS_KM

        nearby = self.get_reporters_in_radius(latitude, longitude, radius_km)
        message = (
            f"[DRISHTI ALERT] Missing: {person.name}, age {person.age}, "
            f"last seen: {person.last_seen_location}. "
            f"If seen, report via DRISHTI app or call 1098."
        )
        dispatches: list[dict] = []
        for reporter in nearby:
            record = {
                "phone": reporter.phone,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            dispatches.append(record)
            self._dispatched_alerts.append(record)
        return dispatches

    # ── Sighting collection ───────────────────────────────────────

    def submit_sighting(self, sighting: Sighting) -> Sighting:
        """Record a community-reported sighting."""
        self._sightings.append(sighting)
        return sighting

    def get_sightings(
        self,
        missing_person_id: Optional[str] = None,
    ) -> list[Sighting]:
        if missing_person_id:
            return [s for s in self._sightings if s.missing_person_id == missing_person_id]
        return list(self._sightings)

    @property
    def dispatched_alerts(self) -> list[dict]:
        return list(self._dispatched_alerts)
