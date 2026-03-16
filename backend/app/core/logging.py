"""
Structured logging configuration for DRISHTI.
"""
import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """Configure application-wide logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    fmt = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(level=log_level, format=fmt, handlers=handlers)
    # Quieten noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
