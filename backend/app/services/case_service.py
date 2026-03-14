"""
Missing person CRUD service with case number generation.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.missing_person import MissingPerson
from app.schemas.missing_person import MissingPersonCreate, MissingPersonUpdate


def _generate_case_number() -> str:
    """Generate a unique case number: DRISHTI-YYYYMMDD-XXXX."""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:6].upper()
    return f"DRISHTI-{today}-{suffix}"


async def create_missing_person(
    db: AsyncSession, data: MissingPersonCreate, officer_id: int
) -> MissingPerson:
    person = MissingPerson(
        case_number=_generate_case_number(),
        assigned_officer_id=officer_id,
        **data.model_dump(),
    )
    db.add(person)
    await db.flush()
    return person


async def get_missing_person(db: AsyncSession, person_id: int) -> Optional[MissingPerson]:
    result = await db.execute(
        select(MissingPerson).where(MissingPerson.id == person_id)
    )
    return result.scalar_one_or_none()


async def get_missing_person_by_case(
    db: AsyncSession, case_number: str
) -> Optional[MissingPerson]:
    result = await db.execute(
        select(MissingPerson).where(MissingPerson.case_number == case_number)
    )
    return result.scalar_one_or_none()


async def list_missing_persons(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    state: Optional[str] = None,
    case_type: Optional[str] = None,
    priority: Optional[str] = None,
) -> tuple[list[MissingPerson], int]:
    query = select(MissingPerson)
    count_query = select(func.count()).select_from(MissingPerson)

    if status:
        query = query.where(MissingPerson.status == status)
        count_query = count_query.where(MissingPerson.status == status)
    if state:
        query = query.where(MissingPerson.state == state)
        count_query = count_query.where(MissingPerson.state == state)
    if case_type:
        query = query.where(MissingPerson.case_type == case_type)
        count_query = count_query.where(MissingPerson.case_type == case_type)
    if priority:
        query = query.where(MissingPerson.priority == priority)
        count_query = count_query.where(MissingPerson.priority == priority)

    query = query.order_by(MissingPerson.created_at.desc()).offset(skip).limit(limit)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query)
    persons = result.scalars().all()
    return list(persons), total


async def update_missing_person(
    db: AsyncSession, person: MissingPerson, data: MissingPersonUpdate
) -> MissingPerson:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(person, field, value)
    await db.flush()
    return person
