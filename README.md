# 👁 DRISHTI

**Distributed Real-time Intelligence System for Human Identification & Trafficking Interception**

A law enforcement and NGO platform to find missing persons and combat human trafficking using AI-powered multimodal identity matching, predictive route analysis, and community intelligence networks.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DRISHTI SYSTEM                              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Police       │  │  Family      │  │  NGO Dashboard           │  │
│  │  Dashboard    │  │  Portal      │  │  (Compliance/Analytics)  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
│         └─────────────────┴──────────────────────┘                 │
│                           │ React Frontend                          │
│                     ┌─────▼──────┐                                  │
│                     │  FastAPI   │                                  │
│                     │  Backend   │                                  │
│                     └─────┬──────┘                                  │
│                           │                                         │
│          ┌────────────────┼────────────────────┐                   │
│          │                │                    │                    │
│  ┌───────▼──────┐ ┌───────▼──────┐ ┌──────────▼──────┐            │
│  │  Module 1    │ │  Module 2    │ │  Module 3        │            │
│  │  Identity    │ │  Route       │ │  Community       │            │
│  │  Engine      │ │  Predictor   │ │  Network         │            │
│  │  (AI/ML)     │ │  (NetworkX)  │ │  (WhatsApp/SMS)  │            │
│  └──────────────┘ └──────────────┘ └──────────────────┘            │
│                                                                     │
│  ┌───────────────┐ ┌──────────────┐ ┌──────────────────┐           │
│  │  Module 4     │ │  Module 5    │ │  Module 6         │           │
│  │  Age          │ │  Transport   │ │  Privacy &        │           │
│  │  Progression  │ │  Hub         │ │  Ethics           │           │
│  │  (GAN)        │ │  Integration │ │  (DPDP Act 2023)  │           │
│  └───────────────┘ └──────────────┘ └──────────────────┘           │
│                           │                                         │
│                     ┌─────▼──────┐                                  │
│                     │  SQLite DB │                                  │
│                     └────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Modules

### Module 1 — Multimodal Identity Engine
Combines multiple biometric signals for person identification:
- **Face Recognition** — DeepFace/ArcFace embeddings (512-dim)
- **Gait Analysis** — OpenGait sequence encoding (works even with disguise)
- **Clothing Analysis** — OpenAI CLIP visual embeddings
- **Body Proportions** — MediaPipe pose landmark analysis
- **Companion Patterns** — Identifies repeat associates/traffickers

Weighted fusion: Face(40%) + Gait(25%) + Body(15%) + Clothing(15%) + Companion(5%)

### Module 2 — Trafficking Route Predictor
Uses NetworkX directed graph of known trafficking corridors:
- **Bengal → Delhi**: Murshidabad → Howrah → Sealdah → NDLS (17–24 hrs)
- **Bihar → Mumbai**: Patna → Varanasi → Allahabad → CSTM (24–30 hrs)
- **Jharkhand → Punjab**: Ranchi → Dhanbad → Delhi → Punjab
- Activates automatic checkpoint alerts along predicted routes

### Module 3 — Community Intelligence Network
- WhatsApp alerts via Twilio to registered community reporters
- Automatic Childline 1098 notification for missing minors
- SMS to gram panchayat officials via e-Panchayat database
- Social media posting (Facebook, Twitter/X)
- Sighting report processing with credibility scoring

### Module 4 — Age Progression Engine
- GAN-based age progression using SAM-Age/InsightFace
- Automatically updates cold case search photos annually
- Celery/APScheduler integration for periodic updates

### Module 5 — Transport Hub Integration
- Railway station CCTV activation (Howrah, Sealdah, NDLS, CSTM)
- Railway Protection Force (RPF) notifications
- Anti-Human Trafficking Unit (AHTU) state-level alerts
- DigiYatra airport biometric system queries
- Border checkpoint alerts (Petrapole, Gede, etc.)

### Module 6 — Privacy & Ethics Architecture
- **DPDP Act 2023** compliance validation
- Audit logging for every data access (officer ID, timestamp, purpose)
- Automated data deletion 30 days after case closure
- Consent management with law enforcement exception documentation
- Quarterly audit reports for Data Protection Board of India

---
DRISHTI is a national AI-powered missing-persons recovery system that connects India's CCTV network, railway stations, and bus terminals into one unified intelligence grid — capable of detecting missing and trafficked individuals in real-time.

## Architecture

```
╔══════════════════════════════════════════════════════╗
║                    DRISHTI CORE                      ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  INPUT LAYER           INTELLIGENCE LAYER            ║
║  ─────────────         ──────────────────            ║
║  CCTV feeds    ──→     Face Recognition Engine       ║
║  Police photos ──→     Age Progression Model         ║
║  Family uploads──→     Gait Recognition              ║
║  Railway cams  ──→     Clothing/Accessory AI         ║
║  Bus terminals ──→     Behavioral Anomaly Detector   ║
║  Community app ──→     Trafficking Route Predictor   ║
║                        Cross-State Alert Network     ║
║                                                      ║
║  OUTPUT LAYER                                        ║
║  ─────────────                                       ║
║  Police dashboard → Real-time sighting alerts        ║
║  Family app      → Location probability heatmap      ║
║  NGO network     → Rescue coordination               ║
║  Railway/bus     → Automated checkpoint flags        ║
╚══════════════════════════════════════════════════════╝
```

## Modules

| Module | Description | Key Technology |
|--------|-------------|----------------|
| **1. Multimodal Identity Engine** | 5 parallel identity signals (face, gait, clothing, body proportions, companion patterns) | DeepFace, ArcFace, OpenGait, CLIP, MediaPipe Pose |
| **2. Trafficking Route Predictor** | Graph-based corridor prediction activating alerts within 60 seconds | NetworkX, XGBoost |
| **3. Community Intelligence Network** | Community reporter fan-out and sighting collection | Twilio WhatsApp Bot |
| **4. AI Age Progression** | Periodic age-progression updates for cold cases | SAM-Age model |
| **5. Transport Hub Integration** | 4-step alert protocol at railway stations, bus terminals, airports | TensorFlow Lite |
| **6. Privacy & Ethics Architecture** | Consent-first, audit trail, decentralised, human-in-loop | DPDP Act 2023 compliant |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Face Recognition | DeepFace + ArcFace |
| Gait Recognition | OpenGait |
| Scene + Clothing | CLIP (OpenAI) |
| Body Landmarks | MediaPipe Pose |
| Route Prediction | NetworkX + XGBoost |
| Community Alerts | Twilio WhatsApp Bot |
| Backend | Python + FastAPI |
| Edge Deployment | TensorFlow Lite |

## Project Structure

```
DRISHTI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy + SQLite
│   │   ├── models/              # ORM: MissingPerson, Alert, AgeProgression
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── modules/             # 6 intelligence modules
│   │   ├── api/                 # REST endpoint routers
│   │   └── utils/               # Helpers (case numbers, Haversine, etc.)
│   ├── tests/                   # 49 pytest tests (all passing)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js               # React Router + navbar
│   │   ├── components/          # Dashboard, Forms, Alerts, Map, Search
│   │   ├── pages/               # Police, Family, NGO portals
│   │   └── services/api.js      # Axios API service layer
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
git clone <repo-url>
cd DRISHTI
docker-compose up --build
```

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs (Swagger): http://localhost:8000/docs

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

**Run Tests:**
```bash
cd backend
python -m pytest tests/ -v
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/missing-persons/` | Register new missing person case |
| `GET`  | `/api/v1/missing-persons/` | List all cases (filter by status/state) |
| `GET`  | `/api/v1/missing-persons/{id}` | Get case details |
| `PATCH`| `/api/v1/missing-persons/{id}/status` | Update case status |
| `POST` | `/api/v1/missing-persons/{id}/photo` | Upload photo |
| `GET`  | `/api/v1/alerts/` | List alerts |
| `POST` | `/api/v1/alerts/` | Create alert |
| `POST` | `/api/v1/alerts/{id}/verify` | Officer verifies alert |
| `POST` | `/api/v1/search/face` | Face recognition search |
| `POST` | `/api/v1/search/multimodal` | Multimodal identity search |
| `GET`  | `/api/v1/search/route/{case_id}` | Get predicted trafficking routes |
| `POST` | `/api/v1/reports/sighting` | Submit community sighting |
| `GET`  | `/api/v1/reports/audit` | Get DPDP compliance audit report |

Full interactive docs available at `/docs` (Swagger UI).

---

## Configuration

Copy and configure environment variables:

```bash
cp backend/.env.example backend/.env
```

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | SQLite path (default: `sqlite:///./drishti.db`) |
| `SECRET_KEY` | JWT signing key — **change in production** |
| `TWILIO_ACCOUNT_SID` | Twilio SID for WhatsApp alerts |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_WHATSAPP_NUMBER` | WhatsApp sender number |
| `GOOGLE_MAPS_API_KEY` | For heatmap integration |
| `FACE_MATCH_THRESHOLD` | Face match confidence threshold (default: 0.6) |

---

## Production ML Setup

The system uses stubs for heavy ML models. Install for production:

```bash
# Face recognition
pip install deepface insightface

# Body pose estimation
pip install mediapipe

# Clothing analysis (CLIP)
pip install torch torchvision
pip install git+https://github.com/openai/CLIP.git

# Age progression
# See: https://github.com/InterDigitalInc/SAM-Age
```

---

## Privacy & Ethics

DRISHTI is designed with privacy-by-default principles:

- **Purpose Limitation**: Data processed only for missing persons investigations
- **Data Minimization**: Only necessary biometric data collected
- **Storage Limitation**: Automatic deletion 30 days post case-closure
- **Transparency**: Full audit trail for every data access
- **DPDP Act 2023**: Compliant with India's data protection law
- **Law Enforcement Exception**: DPDP Act 2023 Section 7(b) documented for each case
- **No Mass Surveillance**: System activated only for specific active cases

Audit reports are generated quarterly and submitted to the Data Protection Board of India.

---

## Helplines

- **100** — Police Emergency
- **1098** — Childline India (missing children)
- **1800-419-0600** — AHTU (Anti-Human Trafficking Unit)
- **1091** — Women's Helpline

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

*DRISHTI is built in partnership with AHTU, NCPCR, and Childline India Foundation.*
