"""
Missing persons case management endpoints.
"""
from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_officer
from app.models.user import User
from app.schemas.missing_person import (
    MissingPersonCreate,
    MissingPersonListResponse,
    MissingPersonResponse,
    MissingPersonUpdate,
)
from app.services.audit_service import log_action
from app.services.case_service import (
    create_missing_person,
    get_missing_person,
    list_missing_persons,
    update_missing_person,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=MissingPersonResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    body: MissingPersonCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
):
    """Register a new missing person case."""
    person = await create_missing_person(db, body, officer.id)
    await log_action(
        db,
        "case_created",
        user_id=officer.id,
        resource_type="missing_person",
        resource_id=person.id,
        details={"case_number": person.case_number, "name": person.full_name},
        request=request,
    )
    return MissingPersonResponse.model_validate(person)


@router.get("/", response_model=MissingPersonListResponse)
async def list_cases(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    case_type: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
):
    """List missing persons cases with pagination and filters."""
    skip = (page - 1) * page_size
    persons, total = await list_missing_persons(
        db,
        skip=skip,
        limit=page_size,
        status=status,
        state=state,
        case_type=case_type,
        priority=priority,
    )
    return MissingPersonListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[MissingPersonResponse.model_validate(p) for p in persons],
    )


@router.get("/{case_id}", response_model=MissingPersonResponse)
async def get_case(
    case_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
):
    """Get a specific missing person case by ID."""
    person = await get_missing_person(db, case_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return MissingPersonResponse.model_validate(person)


@router.patch("/{case_id}", response_model=MissingPersonResponse)
async def update_case(
    case_id: int,
    body: MissingPersonUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    officer: Annotated[User, Depends(require_officer)],
):
    """Update a missing person case."""
    person = await get_missing_person(db, case_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    person = await update_missing_person(db, person, body)
    await log_action(
        db,
        "case_updated",
        user_id=officer.id,
        resource_type="missing_person",
        resource_id=case_id,
        details=body.model_dump(exclude_unset=True),
        request=request,
    )
    return MissingPersonResponse.model_validate(person)
