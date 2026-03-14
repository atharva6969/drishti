"""
Sightings endpoints.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_officer
from app.models.sighting import Sighting
from app.models.user import User
from app.schemas.sighting import SightingCreate, SightingResponse, SightingVerify
from app.services.audit_service import log_action

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SightingResponse, status_code=status.HTTP_201_CREATED)
async def report_sighting(
    body: SightingCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
):
    """Report a sighting of a missing person."""
    sighting = Sighting(**body.model_dump())
    db.add(sighting)
    await db.flush()

    await log_action(
        db,
        "sighting_reported",
        user_id=_user.id,
        resource_type="sighting",
        resource_id=sighting.id,
        details={"missing_person_id": sighting.missing_person_id, "source": sighting.source},
        request=request,
    )
    return SightingResponse.model_validate(sighting)


@router.get("/", response_model=list[SightingResponse])
async def list_sightings(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
    missing_person_id: Optional[int] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """List sightings, optionally filtered by missing person."""
    query = select(Sighting)
    if missing_person_id:
        query = query.where(Sighting.missing_person_id == missing_person_id)
    query = query.order_by(Sighting.sighted_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    sightings = result.scalars().all()
    return [SightingResponse.model_validate(s) for s in sightings]


@router.post("/{sighting_id}/verify", response_model=SightingResponse)
async def verify_sighting(
    sighting_id: int,
    body: SightingVerify,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
):
    """Verify or mark a sighting as false positive (officer only)."""
    result = await db.execute(select(Sighting).where(Sighting.id == sighting_id))
    sighting = result.scalar_one_or_none()
    if not sighting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sighting not found")

    sighting.status = body.status
    sighting.verified_by_id = officer.id
    sighting.verified_at = datetime.now(timezone.utc)
    if body.notes:
        sighting.notes = body.notes

    await db.flush()
    await log_action(
        db,
        "sighting_verified",
        user_id=officer.id,
        resource_type="sighting",
        resource_id=sighting_id,
        details={"status": body.status},
        request=request,
    )
    return SightingResponse.model_validate(sighting)
