"""
Sighting model — confirmed or unconfirmed sightings of missing persons.
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sighting(Base):
    __tablename__ = "sightings"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    missing_person_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("missing_persons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Location
    location_name: Mapped[str | None] = mapped_column(sa.String(500))
    latitude: Mapped[float | None] = mapped_column(sa.Float)
    longitude: Mapped[float | None] = mapped_column(sa.Float)
    location_type: Mapped[str | None] = mapped_column(sa.String(50))
    # railway_station | bus_terminal | airport | street | market | other

    # Source
    source: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    # cctv | community_report | police | railway | airport

    # Reporter (for community sightings)
    reporter_name: Mapped[str | None] = mapped_column(sa.String(200))
    reporter_phone: Mapped[str | None] = mapped_column(sa.String(20))
    reporter_id: Mapped[int | None] = mapped_column(
        sa.Integer, sa.ForeignKey("community_reporters.id", ondelete="SET NULL")
    )

    # Evidence
    photo_url: Mapped[str | None] = mapped_column(sa.String(500))
    confidence_score: Mapped[float | None] = mapped_column(sa.Float)
    identity_signals: Mapped[dict | None] = mapped_column(JSONB)
    # {"face": 0.92, "gait": 0.88, "clothing": 0.75, "body": 0.81}

    # Status
    status: Mapped[str] = mapped_column(
        sa.String(20), default="unverified", nullable=False
    )  # unverified | verified | false_positive
    verified_by_id: Mapped[int | None] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    verified_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(sa.Text)

    sighted_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    missing_person: Mapped["MissingPerson"] = relationship(  # noqa: F821
        "MissingPerson", back_populates="sightings"
    )

    def __repr__(self) -> str:
        return f"<Sighting {self.id} — MP:{self.missing_person_id} @ {self.location_name}>"
