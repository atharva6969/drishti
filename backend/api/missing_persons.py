"""API endpoints for missing-person management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.schemas import CaseStatus, MissingPerson
from backend.modules.privacy import PrivacyManager

router = APIRouter()

# In-memory store shared across requests (MVP; replace with DB).
_privacy = PrivacyManager()


@router.post("/", status_code=201)
def register_missing_person(person: MissingPerson) -> dict:
    """Register a new missing person (consent required)."""
    ok = _privacy.register_person(person)
    if not ok:
        raise HTTPException(status_code=403, detail="Consent not provided")
    return {"id": person.id, "status": "registered"}


@router.get("/{person_id}")
def get_missing_person(person_id: str) -> dict:
    if not _privacy.is_registered(person_id):
        raise HTTPException(status_code=404, detail="Person not found")
    # Simplified: return id + status only (no PII leak in URL traversal)
    return {"id": person_id, "registered": True}


@router.post("/{person_id}/resolve")
def resolve_case(person_id: str, officer_id: str) -> dict:
    ok = _privacy.resolve_case(person_id, officer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"id": person_id, "status": CaseStatus.RESOLVED.value}
