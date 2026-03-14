from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import missing_persons, alerts, search, reports
from app.database import engine, Base

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DRISHTI API",
    description=(
        "Distributed Real-time Intelligence System for Human Identification "
        "& Trafficking Interception — A law enforcement platform for finding "
        "missing persons and combating human trafficking."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - configure for production with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded photos
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(missing_persons.router)
app.include_router(alerts.router)
app.include_router(search.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "system": "DRISHTI",
        "description": "Distributed Real-time Intelligence System for Human Identification & Trafficking Interception",
        "version": "1.0.0",
        "status": "operational",
        "modules": [
            "Multimodal Identity Engine",
            "Trafficking Route Predictor",
            "Community Intelligence Network",
            "Age Progression Engine",
            "Transport Hub Integration",
            "Privacy & Ethics Architecture"
        ],
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}
