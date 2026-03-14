# DRISHTI API Documentation

## Base URL
```
Production:  https://api.drishti.police.gov.in/api/v1
Development: http://localhost:8000/api/v1
```

Interactive documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Authentication

All API endpoints (except `/auth/login`) require a Bearer token.

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "badge_number": "WB-CID-001",
  "password": "your_password"
}
```
**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{ "refresh_token": "eyJhbGci..." }
```

---

## Cases API

### List Cases
```http
GET /cases?status=active&priority=critical&page=1&page_size=20
Authorization: Bearer <token>
```

### Create Case
```http
POST /cases
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Priya Sharma",
  "age_at_disappearance": 16,
  "gender": "female",
  "date_missing": "2024-01-15T08:00:00Z",
  "last_seen_location": "Murshidabad Bus Stand",
  "state": "West Bengal",
  "case_type": "trafficking",
  "priority": "critical",
  "circumstances": "Last seen boarding a bus towards Malda."
}
```
**Response:** `201 Created` with full case object including `case_number`.

### Get Case
```http
GET /cases/{id}
Authorization: Bearer <token>
```

### Update Case
```http
PATCH /cases/{id}
Authorization: Bearer <token>
Content-Type: application/json

{ "status": "found", "priority": "low" }
```

---

## Search API

### Face Search (Multimodal)
```http
POST /search/multimodal
Authorization: Bearer <token>
Content-Type: multipart/form-data

image: <binary>
use_clothing: true
use_body: true
threshold: 0.5
```

**Response:**
```json
{
  "matches": [
    {
      "case_id": 42,
      "case_number": "DRISHTI-20240115-ABC123",
      "full_name": "Priya Sharma",
      "face_score": 0.87,
      "clothing_score": 0.72,
      "body_score": null,
      "combined_score": 0.81,
      "confidence_level": "high"
    }
  ],
  "signals_used": { "face": true, "clothing": true, "body": false },
  "search_time_ms": 234
}
```

### Predict Trafficking Route
```http
POST /search/route-predict/{case_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "case_id": 42,
  "case_number": "DRISHTI-20240115-ABC123",
  "source_location": "Murshidabad",
  "predicted_routes": [
    {
      "route_id": 0,
      "path": ["Murshidabad", "Howrah", "New Delhi"],
      "probability": 0.72,
      "total_hours_min": 21,
      "total_hours_max": 30,
      "checkpoints": [
        {
          "station_id": "HWH",
          "station_name": "Howrah",
          "station_code": "HWH",
          "state": "West Bengal",
          "estimated_arrival_hours_min": 4,
          "estimated_arrival_hours_max": 6,
          "transport_method": "train",
          "alert_priority": "high"
        }
      ]
    }
  ],
  "activation_time_seconds": 0.045
}
```

---

## Sightings API

### Report Sighting
```http
POST /sightings
Authorization: Bearer <token>
Content-Type: application/json

{
  "missing_person_id": 42,
  "sighted_at": "2024-01-15T14:30:00Z",
  "location_name": "Howrah Station Platform 7",
  "latitude": 22.585,
  "longitude": 88.316,
  "source": "community",
  "description": "Person matching description seen with two adults heading to platform 7.",
  "confidence_score": 0.75
}
```

### Verify Sighting
```http
POST /sightings/{id}/verify
Authorization: Bearer <token>
Content-Type: application/json

{ "verified": true, "officer_notes": "Confirmed by RPF officer at station." }
```

---

## Alerts API

### List Alerts
```http
GET /alerts?severity=critical&status=pending
Authorization: Bearer <token>
```

### Acknowledge Alert
```http
POST /alerts/{id}/acknowledge
Authorization: Bearer <token>
```

---

## Community API

### List Reporters
```http
GET /community/reporters?district=Murshidabad&is_verified=true
Authorization: Bearer <token>
```

### Broadcast Alert
```http
POST /community/broadcast/{case_id}?radius_km=50
Authorization: Bearer <token>
```

---

## Error Responses

All errors follow RFC 7807 Problem Details format:
```json
{
  "detail": "Case not found.",
  "type": "not_found",
  "status": 404
}
```

| Code | Description |
|------|-------------|
| 400  | Bad Request — validation error |
| 401  | Unauthorized — invalid/expired token |
| 403  | Forbidden — insufficient role |
| 404  | Not Found |
| 422  | Unprocessable Entity — schema violation |
| 429  | Too Many Requests — rate limited |
| 500  | Internal Server Error |
