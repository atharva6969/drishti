"""
AI-powered search endpoint — multimodal identity matching.
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_officer
from app.models.user import User
from app.services.audit_service import log_action

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/face")
async def search_by_face(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
    image: UploadFile = File(..., description="Image file containing the face to search"),
    threshold: float = Form(default=0.6, ge=0.0, le=1.0),
):
    """
    Search the missing persons database by face.
    Uploads an image and returns matching cases with confidence scores.
    """
    if image.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    image_bytes = await image.read()
    await log_action(
        db,
        "face_search",
        user_id=officer.id,
        resource_type="search",
        details={"filename": image.filename, "threshold": threshold},
        request=request,
    )

    # In production, this calls the ML face recognition service
    # Here we return a stub response to demonstrate the API contract
    return {
        "query_image": image.filename,
        "threshold": threshold,
        "matches": [],
        "search_id": "stub-search-id",
        "note": "ML engine not loaded in stub mode",
    }


@router.post("/multimodal")
async def search_multimodal(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
    image: UploadFile = File(...),
    use_gait: bool = Form(default=False),
    use_clothing: bool = Form(default=True),
    use_body: bool = Form(default=True),
):
    """
    Multimodal search combining face, clothing, and body biometrics.
    Returns ranked matches with per-signal confidence scores.
    """
    image_bytes = await image.read()
    await log_action(
        db,
        "multimodal_search",
        user_id=officer.id,
        resource_type="search",
        details={
            "filename": image.filename,
            "signals": {
                "face": True,
                "gait": use_gait,
                "clothing": use_clothing,
                "body": use_body,
            },
        },
        request=request,
    )

    return {
        "query_image": image.filename,
        "signals_used": {
            "face": True,
            "gait": use_gait,
            "clothing": use_clothing,
            "body": use_body,
        },
        "matches": [],
        "note": "ML engine not loaded in stub mode",
    }


@router.post("/route-predict/{case_id}")
async def predict_trafficking_route(
    case_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
):
    """
    Activate the trafficking route predictor for a given case.
    Returns predicted routes, checkpoints, and time windows.
    """
    from app.services.case_service import get_missing_person

    person = await get_missing_person(db, case_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    await log_action(
        db,
        "route_prediction",
        user_id=officer.id,
        resource_type="missing_person",
        resource_id=case_id,
        request=request,
    )

    # Stub response — real implementation calls route_predictor ML module
    return {
        "case_id": case_id,
        "case_number": person.case_number,
        "source_location": person.last_seen_location,
        "predicted_routes": [
            {
                "route_id": 1,
                "path": ["Murshidabad", "Malda", "Howrah", "New Delhi"],
                "probability": 0.72,
                "transport_method": "train",
                "estimated_hours": {"Murshidabad→Howrah": "4-6", "Howrah→Delhi": "17-24"},
                "checkpoints": [
                    {"station": "Howrah", "code": "HWH", "alert_sent": False},
                    {"station": "New Delhi", "code": "NDLS", "alert_sent": False},
                ],
            }
        ],
        "alert_status": "pending",
        "note": "ML route predictor not loaded in stub mode",
    }
