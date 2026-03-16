"""
Pydantic schemas for alert endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertCreate(BaseModel):
    missing_person_id: int
    alert_type: str
    severity: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    title: str = Field(..., max_length=300)
    message: str
    recipient_type: str
    recipients: Optional[dict] = None
    channel: str = Field(..., pattern="^(push|sms|whatsapp|email|api)$")

    location: str
    confidence_score: float
    source: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

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
    location: str
    confidence_score: float
    status: str
    source: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True

class AlertVerify(BaseModel):
    officer_id: str
    verdict: str  # verified or false_positive
    notes: Optional[str] = None
