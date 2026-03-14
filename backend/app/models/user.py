"""
User model — police officers, AHTU officers, supervisors, admins.
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    badge_number: Mapped[str] = mapped_column(sa.String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        sa.String(20), nullable=False, default="officer"
    )  # officer | supervisor | admin
    department: Mapped[str | None] = mapped_column(sa.String(200))
    state: Mapped[str | None] = mapped_column(sa.String(100))
    phone: Mapped[str | None] = mapped_column(sa.String(20))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
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
    cases: Mapped[list["MissingPerson"]] = relationship(  # noqa: F821
        "MissingPerson", back_populates="assigned_officer", foreign_keys="MissingPerson.assigned_officer_id"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")  # noqa: F821

    def __repr__(self) -> str:
        return f"<User {self.badge_number} ({self.role})>"
