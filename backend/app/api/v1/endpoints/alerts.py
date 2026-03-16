"""
Alerts endpoints.
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
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResponse
from app.services.alert_service import create_alert, dispatch_alert, list_alerts
from app.services.audit_service import log_action

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_new_alert(
    body: AlertCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
):
    """Create and dispatch a new alert."""
    alert = await create_alert(db, body)
    await dispatch_alert(db, alert)
    await log_action(
        db,
        "alert_created",
        user_id=officer.id,
        resource_type="alert",
        resource_id=alert.id,
        details={"alert_type": alert.alert_type, "severity": alert.severity},
        request=request,
    )
    return AlertResponse.model_validate(alert)


@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
    missing_person_id: Optional[int] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """List alerts."""
    alerts = await list_alerts(db, missing_person_id=missing_person_id, skip=skip, limit=limit)
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
):
    """Acknowledge an alert (officer confirms receipt and action)."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by_id = officer.id
    await db.flush()

    await log_action(
        db,
        "alert_acknowledged",
        user_id=officer.id,
        resource_type="alert",
        resource_id=alert_id,
        request=request,
    )
    return AlertResponse.model_validate(alert)
