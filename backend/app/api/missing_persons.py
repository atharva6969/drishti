from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import shutil
import os

from app.database import get_db
from app.models.missing_person import MissingPerson
from app.schemas.missing_person import MissingPersonCreate, MissingPersonResponse, MissingPersonUpdate
from app.utils.helpers import generate_case_number

router = APIRouter(prefix="/api/v1/missing-persons", tags=["Missing Persons"])

UPLOAD_DIR = "uploads/photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=MissingPersonResponse, status_code=201)
def report_missing_person(
    person: MissingPersonCreate,
    db: Session = Depends(get_db)
):
    """Report a new missing person case."""
    case_number = generate_case_number(
        state=person.state or "XX",
        district=person.district or "000"
    )
    
    db_person = MissingPerson(
        **person.model_dump(),
        case_number=case_number
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@router.get("/", response_model=List[MissingPersonResponse])
def list_missing_persons(
    status: Optional[str] = "active",
    state: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all missing person cases."""
    query = db.query(MissingPerson)
    if status:
        query = query.filter(MissingPerson.status == status)
    if state:
        query = query.filter(MissingPerson.state == state)
    return query.offset(skip).limit(limit).all()


@router.get("/{person_id}", response_model=MissingPersonResponse)
def get_missing_person(person_id: int, db: Session = Depends(get_db)):
    """Get details of a specific missing person case."""
    person = db.query(MissingPerson).filter(MissingPerson.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Case not found")
    return person


@router.patch("/{person_id}/status", response_model=MissingPersonResponse)
def update_case_status(
    person_id: int,
    update: MissingPersonUpdate,
    db: Session = Depends(get_db)
):
    """Update case status (found/closed/active)."""
    person = db.query(MissingPerson).filter(MissingPerson.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Case not found")
    
    valid_statuses = {"active", "found", "closed"}
    if update.status and update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    person.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(person)
    return person


@router.post("/{person_id}/photo")
async def upload_photo(
    person_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload photo for a missing person case."""
    person = db.query(MissingPerson).filter(MissingPerson.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Case not found")
    
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{person.case_number}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    person.photo_path = file_path
    db.commit()
    
    return {"status": "uploaded", "photo_path": file_path}
