"""
Pydantic schemas for alert endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    missing_person_id: int
    alert_type: str
    severity: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    title: str = Field(..., max_length=300)
    message: str
    recipient_type: str
    recipients: Optional[dict] = None
    channel: str = Field(..., pattern="^(push|sms|whatsapp|email|api)$")


class AlertResponse(BaseModel):
    id: int
    missing_person_id: int
    alert_type: str
    severity: str
    title: str
    message: str
    recipient_type: str
    channel: str
    status: str
    sent_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
