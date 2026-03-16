"""
Pydantic schemas for missing person endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MissingPersonCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    age_at_disappearance: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(None, ge=30, le=300)
    weight_kg: Optional[float] = Field(None, ge=1, le=500)
    distinguishing_marks: Optional[str] = None
    date_missing: datetime
    last_seen_location: Optional[str] = None
    last_seen_latitude: Optional[float] = Field(None, ge=-90, le=90)
    last_seen_longitude: Optional[float] = Field(None, ge=-180, le=180)
    circumstances: Optional[str] = None
    case_type: str = Field(default="missing", pattern="^(missing|trafficking|runaway|abduction)$")
    priority: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    reporting_station: Optional[str] = None
    state: Optional[str] = None


class MissingPersonUpdate(BaseModel):
    full_name: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(active|found|closed|cold_case)$")
    assigned_officer_id: Optional[int] = None
    circumstances: Optional[str] = None
    notes: Optional[str] = None


class MissingPersonResponse(BaseModel):
    id: int
    case_number: str
    full_name: str
    age_at_disappearance: Optional[int]
    gender: Optional[str]
    date_missing: datetime
    last_seen_location: Optional[str]
    last_seen_latitude: Optional[float]
    last_seen_longitude: Optional[float]
    case_type: str
    priority: str
    status: str
    primary_photo_url: Optional[str]
    age_progressed_photo_url: Optional[str]
    reporting_station: Optional[str]
    state: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MissingPersonListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[MissingPersonResponse]
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
