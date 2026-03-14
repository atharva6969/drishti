"""
Alert model — system-generated alerts dispatched to officers / checkpoints.
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    missing_person_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("missing_persons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    # corridor_activation | sighting_match | checkpoint_alert | community_broadcast

    severity: Mapped[str] = mapped_column(sa.String(20), default="normal", nullable=False)
    # low | normal | high | critical

    title: Mapped[str] = mapped_column(sa.String(300), nullable=False)
    message: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # Recipients
    recipient_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    # officer | railway_police | ahtu | community | family | all

    recipients: Mapped[dict | None] = mapped_column(JSONB)
    # {"station_codes": ["HWH", "NDLS"], "officer_ids": [1, 2, 3]}

    # Delivery
    channel: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    # push | sms | whatsapp | email | api

    status: Mapped[str] = mapped_column(sa.String(20), default="pending", nullable=False)
    # pending | sent | delivered | failed

    sent_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    acknowledged_by_id: Mapped[int | None] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    missing_person: Mapped["MissingPerson"] = relationship(  # noqa: F821
        "MissingPerson", back_populates="alerts"
    )

    def __repr__(self) -> str:
        return f"<Alert {self.id} [{self.alert_type}] MP:{self.missing_person_id}>"
