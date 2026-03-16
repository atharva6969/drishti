"""
Module 3: Community Intelligence Network

Coordinates community reporters, NGOs, panchayats, and
social media platforms for distributed sighting reports.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CommunityNetwork:
    """
    Community Intelligence Network for crowdsourced sighting reports
    and coordinated alerts across civil society.
    """

    def __init__(self):
        self.whatsapp_client = None
        self.sms_client = None
        self._init_clients()
        
        # Mock registry of community reporters
        self.reporter_registry: Dict[str, List[str]] = {
            "West Bengal": ["+91-9000000001", "+91-9000000002"],
            "Bihar": ["+91-9000000003", "+91-9000000004"],
            "Delhi": ["+91-9000000005", "+91-9000000006"],
        }

    def _init_clients(self):
        """Initialize Twilio and SMS clients."""
        try:
            # from twilio.rest import Client
            # self.whatsapp_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            logger.info("WhatsApp client: stub (configure Twilio credentials for production)")
        except Exception as e:
            logger.warning(f"WhatsApp client not initialized: {e}")

    def notify_community_reporters(
        self,
        alert_data: Dict[str, Any],
        location: str,
        radius_km: int = 50
    ) -> Dict[str, Any]:
        """
        Alert community reporters within radius of last known location.
        
        Production: Query PostGIS/spatial DB for reporters within radius,
        then batch send WhatsApp/SMS alerts via Twilio.
        """
        state = alert_data.get("state", "Unknown")
        reporters = self.reporter_registry.get(state, [])
        
        message = self._format_alert_message(alert_data)
        notifications_sent = []
        
        for phone in reporters:
            result = self.send_whatsapp_alert(phone, message)
            notifications_sent.append({
                "phone": phone[-4:].rjust(10, "*"),  # Mask number
                "status": result["status"],
                "channel": "whatsapp"
            })
        
        logger.info(f"Notified {len(notifications_sent)} community reporters in {state}")
        
        return {
            "reporters_notified": len(notifications_sent),
            "location": location,
            "radius_km": radius_km,
            "notifications": notifications_sent,
            "timestamp": datetime.utcnow().isoformat()
        }

    def post_to_social_media(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post alert to Facebook groups, Twitter, and regional social platforms.
        
        Production: Use Facebook Graph API, Twitter/X API v2.
        Target missing persons groups, community pages.
        """
        # Production:
        # facebook_api.post_to_groups(message, target_groups)
        # twitter_api.create_tweet(message)
        
        platforms_posted = ["Facebook (stub)", "Twitter/X (stub)", "Telegram (stub)"]
        
        return {
            "status": "posted",
            "platforms": platforms_posted,
            "message_preview": self._format_alert_message(alert_data)[:100] + "...",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Configure social media API keys for production"
        }

    def notify_childline(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notify Childline 1098 about missing child.
        Triggered automatically for cases involving minors.
        """
        age = alert_data.get("age", 18)
        
        if age >= 18:
            return {
                "status": "skipped",
                "reason": "Person is adult (age >= 18)"
            }
        
        # Production: API call to Childline CMS
        # childline_api.report_case(alert_data)
        
        return {
            "status": "notified",
            "organization": "Childline India Foundation",
            "helpline": "1098",
            "case_reference": alert_data.get("case_number", ""),
            "child_age": age,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Childline API integration required for production"
        }

    def send_sms_to_panchayat(
        self,
        alert_data: Dict[str, Any],
        district: str
    ) -> Dict[str, Any]:
        """
        Send SMS alert to gram panchayat officials in the district.
        Uses government e-Panchayat contact database.
        """
        # Production: Query e-Panchayat database for district contacts
        # sms_gateway.send_bulk(panchayat_contacts, message)
        
        message = (
            f"MISSING PERSON ALERT - {alert_data.get('name', 'Unknown')}, "
            f"Age: {alert_data.get('age', 'Unknown')}, "
            f"Last seen: {alert_data.get('last_seen_location', 'Unknown')}. "
            f"Case: {alert_data.get('case_number', '')}. "
            f"Contact: 100 or local police station."
        )
        
        return {
            "status": "sent",
            "district": district,
            "recipient_type": "gram_panchayat",
            "estimated_recipients": 15,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "SMS gateway integration required for production"
        }

    def process_sighting_report(self, sighting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming sighting report from community member.
        Validates data, enriches with metadata, and triggers alerts.
        """
        required_fields = ["reporter_name", "location", "description"]
        missing_fields = [f for f in required_fields if not sighting_data.get(f)]
        
        if missing_fields:
            return {
                "status": "invalid",
                "missing_fields": missing_fields,
                "message": "Sighting report missing required fields"
            }
        
        processed_report = {
            **sighting_data,
            "report_id": f"SR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "received_at": datetime.utcnow().isoformat(),
            "status": "pending_verification",
            "credibility_score": self._compute_credibility_score(sighting_data),
            "requires_immediate_action": sighting_data.get("confidence", 0) >= 0.7
        }
        
        return {
            "status": "received",
            "report": processed_report,
            "next_steps": [
                "Report forwarded to nearest police station",
                "Verification team will contact you within 30 minutes",
                "Please stay on scene if safe to do so"
            ]
        }

    def send_whatsapp_alert(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp alert via Twilio.
        
        Production: 
        self.whatsapp_client.messages.create(
            from_=f"whatsapp:{settings.twilio_whatsapp_number}",
            body=message,
            to=f"whatsapp:{phone_number}"
        )
        """
        # Production Twilio integration
        # message = self.whatsapp_client.messages.create(...)
        
        logger.info(f"WhatsApp alert sent to {phone_number[-4:].rjust(10, '*')}")
        
        return {
            "status": "sent",
            "channel": "whatsapp",
            "message_length": len(message),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Configure Twilio for production"
        }

    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert data into human-readable message."""
        return (
            f"MISSING PERSON ALERT\n"
            f"Name: {alert_data.get('name', 'Unknown')}\n"
            f"Age: {alert_data.get('age', 'Unknown')} | "
            f"Gender: {alert_data.get('gender', 'Unknown')}\n"
            f"Last seen: {alert_data.get('last_seen_location', 'Unknown')}\n"
            f"Description: {alert_data.get('physical_description', 'N/A')}\n"
            f"Case #: {alert_data.get('case_number', 'N/A')}\n"
            f"If spotted, call 100 immediately. Do NOT approach alone.\n"
            f"DRISHTI System | Powered by AHTU"
        )

    def _compute_credibility_score(self, sighting_data: Dict[str, Any]) -> float:
        """Compute credibility score for a sighting report."""
        score = 0.5  # Base score
        
        if sighting_data.get("photo_attached"):
            score += 0.2
        if sighting_data.get("video_attached"):
            score += 0.2
        if sighting_data.get("verified_reporter"):
            score += 0.1
        if sighting_data.get("location_gps"):
            score += 0.1
        
        return min(score, 1.0)
