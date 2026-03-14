"""Data models for the DRISHTI system."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    """Status of a missing person case."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertPriority(str, Enum):
    """Priority level for an alert."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(str, Enum):
    """Status of an alert."""

    PENDING = "pending"
    DISPATCHED = "dispatched"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class TransportMode(str, Enum):
    """Mode of transport."""

    TRAIN = "train"
    BUS = "bus"
    PRIVATE_VEHICLE = "private_vehicle"
    AIR = "air"
    FOOT = "foot"


# ── Person / Missing Person ──────────────────────────────────────────


class PersonDescription(BaseModel):
    """Physical description used for multimodal matching."""

    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    clothing_description: Optional[str] = None
    distinguishing_features: Optional[str] = None
    last_known_accessories: Optional[str] = None


class MissingPerson(BaseModel):
    """Registered missing person record."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    gender: str
    photo_url: Optional[str] = None
    description: PersonDescription = Field(default_factory=PersonDescription)
    last_seen_location: str
    last_seen_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    reported_by: str
    case_status: CaseStatus = CaseStatus.ACTIVE
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    consent_given: bool = True


# ── Alert ─────────────────────────────────────────────────────────────


class Alert(BaseModel):
    """Alert issued when a potential match is detected."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    missing_person_id: str
    location: str
    confidence: float
    signals_matched: list[str] = Field(default_factory=list)
    priority: AlertPriority = AlertPriority.HIGH
    status: AlertStatus = AlertStatus.PENDING
    officer_id: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    verified: bool = False


# ── Sighting ──────────────────────────────────────────────────────────


class Sighting(BaseModel):
    """Community-reported sighting of a potentially missing person."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    missing_person_id: Optional[str] = None
    reporter_phone: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None
    description: str = ""
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── Route ─────────────────────────────────────────────────────────────


class RouteCheckpoint(BaseModel):
    """A single checkpoint along a trafficking route."""

    location: str
    hub_type: str = "railway_station"
    estimated_arrival_hours: Optional[float] = None


class TraffickingRoute(BaseModel):
    """A predicted trafficking route from source to destination."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    destination: str
    checkpoints: list[RouteCheckpoint] = Field(default_factory=list)
    transport_modes: list[TransportMode] = Field(default_factory=list)
    estimated_total_hours: Optional[float] = None


# ── Audit ─────────────────────────────────────────────────────────────


class AuditEntry(BaseModel):
    """Immutable audit-log entry for every system action."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    officer_id: str
    target_person_id: Optional[str] = None
    details: str = ""
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
