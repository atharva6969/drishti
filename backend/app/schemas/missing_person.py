from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MissingPersonCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    last_seen_location: Optional[str] = None
    last_seen_date: Optional[datetime] = None
    reported_by: Optional[str] = None
    contact_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    physical_description: Optional[str] = None
    clothing_description: Optional[str] = None

class MissingPersonUpdate(BaseModel):
    status: Optional[str] = None
    last_seen_location: Optional[str] = None
    physical_description: Optional[str] = None
    clothing_description: Optional[str] = None

class MissingPersonResponse(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    last_seen_location: Optional[str] = None
    last_seen_date: Optional[datetime] = None
    reported_by: Optional[str] = None
    contact_number: Optional[str] = None
    photo_path: Optional[str] = None
    status: str
    created_at: datetime
    case_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    physical_description: Optional[str] = None
    clothing_description: Optional[str] = None

    class Config:
        from_attributes = True
