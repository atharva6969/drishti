"""Application configuration for DRISHTI system."""

import os


class Settings:
    """Central configuration for DRISHTI backend services."""

    APP_NAME: str = "DRISHTI"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Distributed Real-time Intelligence System "
        "for Human Identification & Trafficking Interception"
    )

    # Privacy settings
    ACTIVE_SEARCH_RETENTION_DAYS: int = 30
    AUDIT_LOG_ENABLED: bool = True
    HUMAN_IN_LOOP_REQUIRED: bool = True

    # Alert configuration
    CORRIDOR_ALERT_TIMEOUT_SECONDS: int = 60
    COMMUNITY_ALERT_RADIUS_KM: float = 50.0
    COMMUNITY_ALERT_MAX_RECIPIENTS: int = 10_000

    # Identity engine thresholds
    FACE_CONFIDENCE_THRESHOLD: float = 0.85
    GAIT_CONFIDENCE_THRESHOLD: float = 0.80
    CLOTHING_CONFIDENCE_THRESHOLD: float = 0.70
    BODY_BIOMETRIC_CONFIDENCE_THRESHOLD: float = 0.75
    COMPANION_CONFIDENCE_THRESHOLD: float = 0.65
    COMBINED_MATCH_THRESHOLD: float = 0.70
    MIN_SIGNALS_FOR_ALERT: int = 2

    # Age progression
    AGE_PROGRESSION_UPDATE_MONTHS: int = 3

    # External service configuration (set via environment)
    TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_FROM: str = os.environ.get("TWILIO_WHATSAPP_FROM", "")


settings = Settings()
