import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import io

from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "DRISHTI"
    assert "modules" in data


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_post_missing_person():
    payload = {
        "name": "Asha Devi",
        "age": 17,
        "gender": "Female",
        "last_seen_location": "Murshidabad Railway Station",
        "reported_by": "Father",
        "contact_number": "+91-9876543210",
        "state": "West Bengal",
        "district": "Murshidabad",
        "physical_description": "5 feet tall, dark hair, brown eyes",
        "clothing_description": "Blue saree"
    }
    
    response = client.post("/api/v1/missing-persons/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Asha Devi"
    assert data["status"] == "active"
    assert data["case_number"] is not None
    assert "DRISHTI" in data["case_number"]


def test_get_missing_persons_empty():
    response = client.get("/api/v1/missing-persons/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_missing_persons_with_data():
    # First create a person
    payload = {
        "name": "Priya Singh",
        "age": 19,
        "state": "Bihar"
    }
    client.post("/api/v1/missing-persons/", json=payload)
    
    response = client.get("/api/v1/missing-persons/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Priya Singh"


def test_get_missing_person_by_id():
    # Create person
    payload = {"name": "Ravi Kumar", "age": 22, "state": "Jharkhand"}
    create_response = client.post("/api/v1/missing-persons/", json=payload)
    person_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/missing-persons/{person_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Ravi Kumar"


def test_get_missing_person_not_found():
    response = client.get("/api/v1/missing-persons/99999")
    assert response.status_code == 404


def test_update_case_status():
    # Create person
    payload = {"name": "Sunita Kumari", "age": 16}
    create_response = client.post("/api/v1/missing-persons/", json=payload)
    person_id = create_response.json()["id"]
    
    # Update status to found
    update_response = client.patch(
        f"/api/v1/missing-persons/{person_id}/status",
        json={"status": "found"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "found"


def test_update_case_status_invalid():
    payload = {"name": "Test Person", "age": 20}
    create_response = client.post("/api/v1/missing-persons/", json=payload)
    person_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/v1/missing-persons/{person_id}/status",
        json={"status": "invalid_status"}
    )
    assert response.status_code == 400


def test_get_alerts_empty():
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_alert():
    # Create missing person first
    person_payload = {"name": "Alert Test Person", "age": 20}
    person_response = client.post("/api/v1/missing-persons/", json=person_payload)
    person_id = person_response.json()["id"]
    
    alert_payload = {
        "missing_person_id": person_id,
        "alert_type": "face_match",
        "location": "Howrah Station",
        "confidence_score": 0.82,
        "source": "camera_HWH_14",
        "description": "Strong face match detected"
    }
    
    response = client.post("/api/v1/alerts/", json=alert_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["alert_type"] == "face_match"
    assert data["status"] == "pending"


def test_verify_alert():
    # Setup: create person and alert
    person_response = client.post("/api/v1/missing-persons/", json={"name": "Verify Test", "age": 18})
    person_id = person_response.json()["id"]
    
    alert_response = client.post("/api/v1/alerts/", json={
        "missing_person_id": person_id,
        "alert_type": "face_match",
        "location": "Station",
        "confidence_score": 0.75
    })
    alert_id = alert_response.json()["id"]
    
    # Verify the alert
    response = client.post(
        f"/api/v1/alerts/{alert_id}/verify",
        json={"officer_id": "OFF-001", "verdict": "verified"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "verified"


def test_post_sighting_report():
    response = client.post("/api/v1/reports/sighting", json={
        "reporter_name": "Helpful Citizen",
        "location": "Sealdah Station",
        "description": "Saw someone matching missing child description near food stall",
        "confidence": 0.6
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    assert "report" in data


def test_post_sighting_report_invalid():
    response = client.post("/api/v1/reports/sighting", json={
        "reporter_name": "Someone"
        # Missing location and description
    })
    
    assert response.status_code == 422  # Pydantic validation error for required fields


def test_search_face():
    fake_image = io.BytesIO(b"fake image data for testing")
    
    response = client.post(
        "/api/v1/search/face",
        params={"officer_id": "OFF-TEST-001"},
        files={"file": ("test.jpg", fake_image, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "search_type" in data
    assert data["search_type"] == "face_recognition"
    assert "matches" in data


def test_get_predicted_routes():
    # Create missing person with West Bengal location
    payload = {
        "name": "Route Test Person",
        "age": 16,
        "state": "West Bengal",
        "last_seen_location": "Murshidabad"
    }
    create_response = client.post("/api/v1/missing-persons/", json=payload)
    person_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/search/route/{person_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "predicted_routes" in data
    assert "corridor_alert" in data
    assert data["person_name"] == "Route Test Person"


def test_audit_report():
    response = client.get("/api/v1/reports/audit")
    assert response.status_code == 200
    data = response.json()
    assert "total_searches" in data
    assert "compliance_status" in data
