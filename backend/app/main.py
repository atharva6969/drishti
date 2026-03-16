"""
DRISHTI Backend - FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import settings
from app.core.database import engine, Base
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting DRISHTI API server v%s", settings.APP_VERSION)
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
    yield
    logger.info("Shutting down DRISHTI API server")

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
        "& Trafficking Interception — REST API"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    """Liveness probe endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness probe endpoint."""
    return {"status": "ready", "version": settings.APP_VERSION}
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
