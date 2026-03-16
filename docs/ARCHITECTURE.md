# DRISHTI Architecture

## Overview

DRISHTI follows a **microservices-oriented monolith** (modular monolith) architecture
that can be decomposed into true microservices as scale demands.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DRISHTI PLATFORM                            │
├──────────────┬───────────────────────┬──────────────────────────────┤
│  INPUT LAYER │  INTELLIGENCE LAYER   │  OUTPUT LAYER                │
│              │                       │                              │
│  CCTV feeds  │  Face Recognition     │  Police Dashboard            │
│  Photos      │  (DeepFace + ArcFace) │  (React + Google Maps)       │
│  WhatsApp    │                       │                              │
│  Community   │  Gait Recognition     │  Mobile Alerts               │
│  Railway     │  (OpenGait)           │  (WhatsApp + SMS)            │
│  cameras     │                       │                              │
│              │  Clothing Detection   │  Railway Control Room        │
│              │  (CLIP)               │                              │
│              │                       │  Family App                  │
│              │  Body Biometrics      │                              │
│              │  (MediaPipe Pose)     │  NGO Network                 │
│              │                       │                              │
│              │  Route Predictor      │  AHTU Officers               │
│              │  (NetworkX + XGBoost) │                              │
│              │                       │                              │
│              │  Age Progression      │  Childline 1098              │
│              │  (SAM-Age)            │                              │
└──────────────┴───────────────────────┴──────────────────────────────┘
```

## System Components

### 1. FastAPI Backend (`backend/app/`)
- **Main application** — FastAPI with async SQLAlchemy
- **Authentication** — JWT with bcrypt password hashing
- **Database** — PostgreSQL (production), SQLite (development)
- **Task queue** — Celery + Redis for async alert dispatch

### 2. ML Pipeline (`backend/ml/`)
Each ML engine is isolated and can be swapped independently:

| Module | Model | Accuracy | Fallback |
|--------|-------|----------|---------|
| Face Recognition | DeepFace + ArcFace | ~99% clean, ~70% occluded | Embedding stub |
| Gait Recognition | OpenGait | ~94% at 10m | GEI + cosine similarity |
| Clothing Detection | CLIP ViT-B/32 | ~85% | CLIP embedding stub |
| Body Biometrics | MediaPipe Pose | ~80% height est. | Landmark stub |
| Route Predictor | NetworkX + XGBoost | N/A | Static route database |
| Age Progression | SAM-Age | State-of-art | No output |

### 3. React Dashboard (`frontend/src/`)
- **Pages:** Dashboard, Cases, Search, Alerts, Map, Community
- **State:** Redux Toolkit + React Query
- **Maps:** Leaflet with OpenStreetMap (no Google API key required)
- **Real-time:** Socket.IO for live alert push

### 4. Community App (`community-app/`)
WhatsApp-first community reporter interface backed by Twilio.

### 5. Edge Deployment (`edge-deployment/`)
TensorFlow Lite models for deployment on existing CCTV hardware.

## Data Flow

```
Missing Person Reported
        │
        ▼
POST /cases  →  case_service.create_missing_person()
        │              │
        │              ├── Generate DRISHTI-YYYYMMDD-XXXXXX case number
        │              ├── Store in PostgreSQL
        │              └── Trigger background tasks (Celery):
        │                     ├── route_predictor.predict_routes()
        │                     │       └── Alert railway police at checkpoints
        │                     ├── community_service.broadcast_alert()
        │                     │       └── WhatsApp/SMS to reporters in radius
        │                     └── alert_service.create_system_alert()
        │
Photo Uploaded
        │
        ▼
POST /cases/{id}/photos  →  Store in S3 / local
        │
        ▼
ML Pipeline (async):
  face_engine.extract_embedding()      → Store in DB
  clothing_engine.extract_features()  → Store in DB
  body_engine.extract_metrics()       → Store in DB

CCTV Frame Arrives
        │
        ▼
POST /search/multimodal  →  multimodal_engine.search()
        │                        │
        │                        ├── face_engine.compare_embeddings()
        │                        ├── clothing_engine.compare()
        │                        └── body_engine.compare()
        │
        ▼
If combined_score ≥ 0.5:
  → Create SightingAlert
  → Push to officer dashboard (WebSocket)
  → Send WhatsApp to assigned officer
  → Log audit entry
```

## Security Architecture

```
DRISHTI Privacy Safeguards
├── Consent-First Database
│   └── Only processes registered missing persons
├── No Live Tracking
│   └── Activates only on missing person query
├── Audit Trail
│   ├── Every search logged with officer_id + timestamp
│   └── DPDP Act 2023 compliant audit retention
├── Role-Based Access Control
│   ├── officer — view and search cases
│   ├── supervisor — modify cases, manage officers
│   └── admin — full access, audit viewing
├── Decentralized (future)
│   └── Federated matching — face embeddings stay in source state
└── Human-in-Loop
    └── AI flags, officer decides — no automated action
```

## Database Schema

```
users ──────────────────── missing_persons
  id                          id
  badge_number                case_number
  full_name                   assigned_officer_id ──→ users.id
  role                        full_name
  email                       status
  password_hash               priority
                              case_type
                              date_missing
                              last_seen_location
                              face_embedding (BYTEA)
                              clothing_features (JSONB)

                              ↓ has many
sightings                   alerts
  id                          id
  missing_person_id           missing_person_id
  sighted_at                  alert_type
  location_name               severity
  latitude / longitude        channel
  source                      status
  confidence_score            acknowledged_at
  status

audit_logs
  id
  user_id
  action
  resource_type / resource_id
  ip_address
  created_at
```
