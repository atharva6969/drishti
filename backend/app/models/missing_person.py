"""
MissingPerson model — core case record.
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MissingPerson(Base):
    __tablename__ = "missing_persons"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    case_number: Mapped[str] = mapped_column(sa.String(50), unique=True, index=True, nullable=False)

    # Personal information
    full_name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    age_at_disappearance: Mapped[int | None] = mapped_column(sa.Integer)
    date_of_birth: Mapped[datetime | None] = mapped_column(sa.Date)
    gender: Mapped[str | None] = mapped_column(sa.String(20))
    height_cm: Mapped[float | None] = mapped_column(sa.Float)
    weight_kg: Mapped[float | None] = mapped_column(sa.Float)
    skin_tone: Mapped[str | None] = mapped_column(sa.String(50))
    distinguishing_marks: Mapped[str | None] = mapped_column(sa.Text)

    # Disappearance details
    date_missing: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    last_seen_location: Mapped[str | None] = mapped_column(sa.String(500))
    last_seen_latitude: Mapped[float | None] = mapped_column(sa.Float)
    last_seen_longitude: Mapped[float | None] = mapped_column(sa.Float)
    circumstances: Mapped[str | None] = mapped_column(sa.Text)

    # Classification
    case_type: Mapped[str] = mapped_column(
        sa.String(50), default="missing", nullable=False
    )  # missing | trafficking | runaway | abduction
    priority: Mapped[str] = mapped_column(
        sa.String(20), default="normal", nullable=False
    )  # low | normal | high | critical
    status: Mapped[str] = mapped_column(
        sa.String(20), default="active", nullable=False
    )  # active | found | closed | cold_case

    # ML / biometric data (stored encrypted)
    face_embedding: Mapped[dict | None] = mapped_column(JSONB)
    gait_signature: Mapped[dict | None] = mapped_column(JSONB)
    clothing_features: Mapped[dict | None] = mapped_column(JSONB)
    body_metrics: Mapped[dict | None] = mapped_column(JSONB)

    # Media
    primary_photo_url: Mapped[str | None] = mapped_column(sa.String(500))
    age_progressed_photo_url: Mapped[str | None] = mapped_column(sa.String(500))
    age_progressed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    # Assignment
    assigned_officer_id: Mapped[int | None] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    reporting_station: Mapped[str | None] = mapped_column(sa.String(200))
    state: Mapped[str | None] = mapped_column(sa.String(100))

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    assigned_officer: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="cases", foreign_keys=[assigned_officer_id]
    )
    sightings: Mapped[list["Sighting"]] = relationship("Sighting", back_populates="missing_person")  # noqa: F821
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="missing_person")  # noqa: F821

    def __repr__(self) -> str:
        return f"<MissingPerson {self.case_number} — {self.full_name}>"
