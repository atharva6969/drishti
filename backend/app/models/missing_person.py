from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class MissingPerson(Base):
    __tablename__ = "missing_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    last_seen_location = Column(String)
    last_seen_date = Column(DateTime)
    reported_by = Column(String)
    contact_number = Column(String)
    photo_path = Column(String)
    status = Column(String, default="active")  # active, found, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    case_number = Column(String, unique=True, index=True)
    state = Column(String)
    district = Column(String)
    physical_description = Column(Text)
    clothing_description = Column(Text)
    
    alerts = relationship("Alert", back_populates="missing_person")
    age_progressions = relationship("AgeProgression", back_populates="missing_person")


class AgeProgression(Base):
    __tablename__ = "age_progressions"
    
    id = Column(Integer, primary_key=True, index=True)
    missing_person_id = Column(Integer, ForeignKey("missing_persons.id"))
    original_age = Column(Integer)
    progressed_age = Column(Integer)
    photo_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    missing_person = relationship("MissingPerson", back_populates="age_progressions")
