from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    missing_person_id = Column(Integer, ForeignKey("missing_persons.id"))
    alert_type = Column(String)  # face_match, gait_match, clothing_match, sighting
    location = Column(String)
    confidence_score = Column(Float)
    status = Column(String, default="pending")  # pending, verified, false_positive
    source = Column(String)  # camera_id, community_reporter, transport_hub
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_by = Column(String)
    verified_at = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    
    missing_person = relationship("MissingPerson", back_populates="alerts")
