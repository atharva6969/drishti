"""
Alert service — creates and dispatches alerts via various channels.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate

logger = logging.getLogger(__name__)


async def create_alert(db: AsyncSession, data: AlertCreate) -> Alert:
    alert = Alert(**data.model_dump())
    db.add(alert)
    await db.flush()
    logger.info("Alert created: %s [%s]", alert.id, alert.alert_type)
    return alert


async def dispatch_alert(db: AsyncSession, alert: Alert) -> bool:
    """
    Dispatch alert through the configured channel.
    Returns True on success.
    In production this would call Twilio, FCM, SMTP, etc.
    """
    try:
        if alert.channel == "sms":
            await _send_sms(alert)
        elif alert.channel == "whatsapp":
            await _send_whatsapp(alert)
        elif alert.channel == "email":
            await _send_email(alert)
        else:
            logger.info("Alert %s queued for channel: %s", alert.id, alert.channel)

        alert.status = "sent"
        alert.sent_at = datetime.now(timezone.utc)
        await db.flush()
        return True
    except Exception as exc:
        logger.error("Failed to dispatch alert %s: %s", alert.id, exc)
        alert.status = "failed"
        await db.flush()
        return False


async def _send_sms(alert: Alert) -> None:
    """Send SMS via Twilio (stub — real implementation requires Twilio credentials)."""
    logger.info("[SMS] Would send: %s", alert.title)


async def _send_whatsapp(alert: Alert) -> None:
    """Send WhatsApp message via Twilio (stub)."""
    logger.info("[WhatsApp] Would send: %s", alert.title)


async def _send_email(alert: Alert) -> None:
    """Send email via SMTP (stub)."""
    logger.info("[Email] Would send: %s", alert.title)


async def list_alerts(
    db: AsyncSession,
    missing_person_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Alert]:
    query = select(Alert)
    if missing_person_id:
        query = query.where(Alert.missing_person_id == missing_person_id)
    query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())
