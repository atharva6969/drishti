from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertCreate(BaseModel):
    missing_person_id: int
    alert_type: str
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
