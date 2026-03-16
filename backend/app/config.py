from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DRISHTI"
    database_url: str = "sqlite:///./drishti.db"
    secret_key: str = "drishti-secret-key-change-in-production"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    google_maps_api_key: str = ""
    alert_radius_km: int = 50
    max_community_reporters: int = 10000
    face_match_threshold: float = 0.6
    confidence_threshold: float = 0.4
    
    class Config:
        env_file = ".env"

settings = Settings()
