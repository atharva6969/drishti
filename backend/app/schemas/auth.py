"""
Pydantic schemas for authentication endpoints.
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    badge_number: str = Field(..., description="Officer badge number")
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    badge_number: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8)
    role: str = Field(default="officer", pattern="^(officer|supervisor|admin)$")
    department: str | None = None
    state: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    badge_number: str
    email: str
    full_name: str
    role: str
    department: str | None
    state: str | None
    is_active: bool

    model_config = {"from_attributes": True}
