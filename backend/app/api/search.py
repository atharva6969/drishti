from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import shutil
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models.missing_person import MissingPerson
from app.modules.identity_engine import IdentityEngine
from app.modules.route_predictor import RoutePredictor
from app.modules.privacy_audit import PrivacyAuditLogger

router = APIRouter(prefix="/api/v1/search", tags=["Search"])

identity_engine = IdentityEngine()
route_predictor = RoutePredictor()
audit_logger = PrivacyAuditLogger()

SEARCH_UPLOAD_DIR = "uploads/search_queries"
os.makedirs(SEARCH_UPLOAD_DIR, exist_ok=True)


@router.post("/face")
async def search_by_face(
    officer_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Search for missing person by face image.
    Runs face analysis and returns ranked matches.
    """
    # Audit log the search
    audit_logger.log_search(
        officer_id=officer_id,
        case_id="face_search",
        search_type="face_recognition",
        timestamp=datetime.utcnow()
    )
    
    # Save uploaded image temporarily
    temp_filename = f"{uuid.uuid4()}.jpg"
    temp_path = os.path.join(SEARCH_UPLOAD_DIR, temp_filename)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        face_analysis = identity_engine.analyze_face(temp_path)
        
        # In production: compare embedding against database
        # matches = db_vector_search(face_analysis["embedding"])
        
        active_cases = db.query(MissingPerson).filter(
            MissingPerson.status == "active"
        ).limit(10).all()
        
        mock_matches = []
        for person in active_cases:
            mock_matches.append({
                "case_id": person.id,
                "case_number": person.case_number,
                "name": person.name,
                "age": person.age,
                "confidence": 0.72,
                "match_type": "face_recognition",
                "last_seen_location": person.last_seen_location
            })
        
        return {
            "search_type": "face_recognition",
            "query_analysis": face_analysis,
            "matches": mock_matches,
            "total_matches": len(mock_matches),
            "searched_at": datetime.utcnow().isoformat()
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/multimodal")
async def search_multimodal(
    officer_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Multimodal identity search combining face, clothing, and body analysis.
    """
    audit_logger.log_search(
        officer_id=officer_id,
        case_id="multimodal_search",
        search_type="multimodal",
        timestamp=datetime.utcnow()
    )
    
    temp_filename = f"{uuid.uuid4()}.jpg"
    temp_path = os.path.join(SEARCH_UPLOAD_DIR, temp_filename)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        full_analysis = identity_engine.identify_person(temp_path)
        
        return {
            "search_type": "multimodal",
            "analysis": full_analysis,
            "matches": [],
            "searched_at": datetime.utcnow().isoformat()
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/route/{case_id}")
def get_predicted_routes(case_id: int, db: Session = Depends(get_db)):
    """Get predicted trafficking routes for a missing person case."""
    person = db.query(MissingPerson).filter(MissingPerson.id == case_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Case not found")
    
    profile = {
        "name": person.name,
        "case_number": person.case_number,
        "last_seen_location": person.last_seen_location or "",
        "state": person.state or "",
        "district": person.district or "",
        "age": person.age
    }
    
    routes = route_predictor.predict_likely_routes(profile)
    corridor_alert = route_predictor.activate_corridor_alert(profile)
    
    return {
        "case_id": case_id,
        "case_number": person.case_number,
        "person_name": person.name,
        "predicted_routes": routes,
        "corridor_alert": corridor_alert,
        "generated_at": datetime.utcnow().isoformat()
    }
