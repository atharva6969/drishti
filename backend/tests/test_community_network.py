import pytest
from app.modules.community_network import CommunityNetwork


@pytest.fixture
def network():
    return CommunityNetwork()


def test_process_valid_sighting_report(network):
    sighting = {
        "reporter_name": "Ramesh Kumar",
        "reporter_phone": "+91-9876543210",
        "location": "Howrah Station, Platform 14",
        "description": "Saw a young girl matching description, appeared scared",
        "confidence": 0.7,
        "photo_attached": False,
        "case_number": "DRISHTI-WB-20240101-ABCD"
    }
    
    result = network.process_sighting_report(sighting)
    
    assert result["status"] == "received"
    assert "report" in result
    assert "next_steps" in result
    assert result["report"]["status"] == "pending_verification"


def test_process_invalid_sighting_report_missing_fields(network):
    sighting = {
        "reporter_name": "Someone"
        # Missing required fields: location, description
    }
    
    result = network.process_sighting_report(sighting)
    
    assert result["status"] == "invalid"
    assert "missing_fields" in result
    assert "location" in result["missing_fields"]
    assert "description" in result["missing_fields"]


def test_notify_community_reporters(network):
    alert_data = {
        "name": "Test Person",
        "age": 16,
        "gender": "Female",
        "last_seen_location": "Kolkata",
        "state": "West Bengal",
        "case_number": "TEST-001"
    }
    
    result = network.notify_community_reporters(
        alert_data=alert_data,
        location="Kolkata",
        radius_km=50
    )
    
    assert "reporters_notified" in result
    assert "location" in result
    assert "radius_km" in result
    assert result["radius_km"] == 50


def test_notify_childline_for_minor(network):
    alert_data = {
        "name": "Minor Child",
        "age": 14,
        "case_number": "TEST-001"
    }
    
    result = network.notify_childline(alert_data)
    
    assert result["status"] == "notified"
    assert "1098" in result["helpline"]


def test_notify_childline_skipped_for_adult(network):
    alert_data = {
        "name": "Adult Person",
        "age": 25,
        "case_number": "TEST-001"
    }
    
    result = network.notify_childline(alert_data)
    
    assert result["status"] == "skipped"


def test_send_sms_to_panchayat(network):
    alert_data = {
        "name": "Test Person",
        "age": 20,
        "last_seen_location": "Rural Area",
        "case_number": "TEST-001"
    }
    
    result = network.send_sms_to_panchayat(alert_data, "Murshidabad")
    
    assert result["status"] == "sent"
    assert result["district"] == "Murshidabad"
    assert "message" in result


def test_send_whatsapp_alert(network):
    result = network.send_whatsapp_alert(
        "+91-9876543210",
        "Test alert message"
    )
    
    assert result["status"] == "sent"
    assert result["channel"] == "whatsapp"


def test_post_to_social_media(network):
    alert_data = {
        "name": "Test Person",
        "age": 18,
        "last_seen_location": "Delhi",
        "case_number": "TEST-001"
    }
    
    result = network.post_to_social_media(alert_data)
    
    assert result["status"] == "posted"
    assert "platforms" in result
    assert len(result["platforms"]) > 0


def test_sighting_credibility_with_photo(network):
    sighting = {
        "reporter_name": "Verified Reporter",
        "location": "Station",
        "description": "Saw person",
        "photo_attached": True,
        "verified_reporter": True,
        "location_gps": True,
        "confidence": 0.8
    }
    
    result = network.process_sighting_report(sighting)
    assert result["status"] == "received"
    assert result["report"]["credibility_score"] > 0.5
