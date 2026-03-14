import uuid
import hashlib
from datetime import datetime
from typing import Optional


def generate_case_number(state: str = "XX", district: str = "000") -> str:
    """Generate unique case number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:4].upper()
    state_code = (state[:2] if state else "XX").upper()
    return f"DRISHTI-{state_code}-{timestamp}-{unique_id}"


def compute_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute approximate distance between two GPS coordinates (Haversine)."""
    import math
    
    R = 6371  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sanitize_phone_number(phone: str) -> str:
    """Normalize Indian phone numbers to +91XXXXXXXXXX format."""
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    return phone


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last N characters."""
    if len(data) <= visible_chars:
        return "*" * len(data)
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]
