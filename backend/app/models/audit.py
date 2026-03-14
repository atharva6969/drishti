"""
AuditLog model — immutable record of all officer actions (DPDP Act compliance).
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(sa.String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(sa.String(50))
    resource_id: Mapped[str | None] = mapped_column(sa.String(100))
    details: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(sa.String(45))
    user_agent: Mapped[str | None] = mapped_column(sa.String(500))
    timestamp: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="audit_logs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AuditLog {self.id} {self.action} by user:{self.user_id}>"


class CommunityReporter(Base):
    """Verified community reporter who can submit sightings."""

    __tablename__ = "community_reporters"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    phone: Mapped[str] = mapped_column(sa.String(20), unique=True, index=True, nullable=False)
    whatsapp_id: Mapped[str | None] = mapped_column(sa.String(50))
    location_district: Mapped[str | None] = mapped_column(sa.String(100))
    location_state: Mapped[str | None] = mapped_column(sa.String(100))
    latitude: Mapped[float | None] = mapped_column(sa.Float)
    longitude: Mapped[float | None] = mapped_column(sa.Float)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    total_sightings: Mapped[int] = mapped_column(sa.Integer, default=0)
    valid_sightings: Mapped[int] = mapped_column(sa.Integer, default=0)
    joined_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CommunityReporter {self.id} — {self.name}>"
