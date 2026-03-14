"""
Community intelligence endpoints — WhatsApp webhook, reporter management.
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_officer
from app.models.audit import CommunityReporter
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Twilio WhatsApp webhook — receives incoming messages from community reporters.
    Processes sighting reports submitted via WhatsApp.
    """
    form_data = await request.form()
    from_number = form_data.get("From", "")
    body = form_data.get("Body", "")
    num_media = int(form_data.get("NumMedia", 0))

    logger.info("WhatsApp message from %s: %s (media: %d)", from_number, body[:50], num_media)

    # In production, this parses the message, extracts sighting info,
    # geocodes the location, and creates a Sighting record
    # For the stub, we return a TwiML response
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Thank you for your report. DRISHTI team will review it shortly. 
    Reference: COMMUNITY-REPORT-RECEIVED</Message>
</Response>"""

    from fastapi.responses import Response
    return Response(content=twiml_response, media_type="application/xml")


@router.get("/reporters", response_model=list[dict])
async def list_reporters(
    db: Annotated[AsyncSession, Depends(get_db)],
    _officer: Annotated[User, Depends(require_officer)],
    skip: int = 0,
    limit: int = 50,
):
    """List verified community reporters."""
    result = await db.execute(
        select(CommunityReporter)
        .where(CommunityReporter.is_active == True)  # noqa: E712
        .offset(skip)
        .limit(limit)
    )
    reporters = result.scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "district": r.location_district,
            "state": r.location_state,
            "is_verified": r.is_verified,
            "total_sightings": r.total_sightings,
            "valid_sightings": r.valid_sightings,
        }
        for r in reporters
    ]


@router.post("/broadcast/{case_id}")
async def broadcast_alert(
    case_id: int,
    radius_km: float = 50.0,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    officer: Annotated[User, Depends(require_officer)] = None,
):
    """
    Broadcast a missing person alert to all community reporters within radius_km.
    """
    from app.services.case_service import get_missing_person
    from app.services.audit_service import log_action

    person = await get_missing_person(db, case_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    await log_action(
        db,
        "community_broadcast",
        user_id=officer.id,
        resource_type="missing_person",
        resource_id=case_id,
        details={"radius_km": radius_km},
    )

    # Stub: in production, query reporters within radius and send Twilio messages
    return {
        "case_id": case_id,
        "case_number": person.case_number,
        "radius_km": radius_km,
        "reporters_notified": 0,
        "status": "queued",
        "note": "Twilio integration requires credentials in .env",
    }
