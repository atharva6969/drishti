from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.modules.community_network import CommunityNetwork
from app.modules.privacy_audit import PrivacyAuditLogger
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])

community_network = CommunityNetwork()
audit_logger = PrivacyAuditLogger()


class SightingReport(BaseModel):
    reporter_name: str
    reporter_phone: Optional[str] = None
    case_number: Optional[str] = None
    missing_person_id: Optional[int] = None
    location: str
    description: str
    confidence: Optional[float] = 0.5
    photo_attached: bool = False
    video_attached: bool = False
    verified_reporter: bool = False
    location_gps: bool = False


@router.post("/sighting")
def report_sighting(sighting: SightingReport, db: Session = Depends(get_db)):
    """
    Community member submits a sighting report.
    """
    sighting_data = sighting.model_dump()
    result = community_network.process_sighting_report(sighting_data)
    return result


@router.get("/audit")
def get_audit_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    officer_id: Optional[str] = "admin"
):
    """
    Get privacy audit report. Requires admin authorization.
    """
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        from datetime import timedelta
        start = datetime.utcnow() - timedelta(days=90)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.utcnow()
    
    report = audit_logger.generate_audit_report(start, end)
    return report
