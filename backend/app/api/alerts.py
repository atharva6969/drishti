from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse, AlertVerify

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = None,
    missing_person_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List alerts with optional filtering."""
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if missing_person_id:
        query = query.filter(Alert.missing_person_id == missing_person_id)
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=AlertResponse, status_code=201)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert."""
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.post("/{alert_id}/verify", response_model=AlertResponse)
def verify_alert(
    alert_id: int,
    verification: AlertVerify,
    db: Session = Depends(get_db)
):
    """Officer verifies or dismisses an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    valid_verdicts = {"verified", "false_positive"}
    if verification.verdict not in valid_verdicts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verdict. Must be one of: {valid_verdicts}"
        )
    
    alert.status = verification.verdict
    alert.verified_by = verification.officer_id
    alert.verified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    return alert
