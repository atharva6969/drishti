"""
Pydantic schemas for sighting endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SightingCreate(BaseModel):
    missing_person_id: int
    location_name: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    location_type: Optional[str] = None
    source: str = Field(..., pattern="^(cctv|community_report|police|railway|airport)$")
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    identity_signals: Optional[dict] = None
    notes: Optional[str] = None
    sighted_at: datetime


class SightingVerify(BaseModel):
    status: str = Field(..., pattern="^(verified|false_positive)$")
    notes: Optional[str] = None


class SightingResponse(BaseModel):
    id: int
    missing_person_id: int
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    location_type: Optional[str]
    source: str
    reporter_name: Optional[str]
    confidence_score: Optional[float]
    identity_signals: Optional[dict]
    status: str
    sighted_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
