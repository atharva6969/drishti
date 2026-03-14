# DRISHTI

**Distributed Real-time Intelligence System for Human Identification & Trafficking Interception**

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
│   ├── main.py                  # FastAPI application entry-point
│   ├── config.py                # Central configuration
│   ├── api/                     # REST API endpoints
│   │   ├── missing_persons.py   # Missing person registration & resolution
│   │   ├── alerts.py            # Transport hub alert management
│   │   ├── sightings.py         # Community sighting submission
│   │   └── routes.py            # Trafficking route prediction
│   ├── models/
│   │   └── schemas.py           # Pydantic data models
│   ├── modules/
│   │   ├── identity_engine.py   # Module 1 — Multimodal Identity Engine
│   │   ├── route_predictor.py   # Module 2 — Trafficking Route Predictor
│   │   ├── community_network.py # Module 3 — Community Intelligence Network
│   │   ├── age_progression.py   # Module 4 — AI Age Progression
│   │   ├── transport_hub.py     # Module 5 — Transport Hub Integration
│   │   └── privacy.py           # Module 6 — Privacy & Ethics Architecture
│   └── utils/
│       └── audit.py             # Audit logging utilities
├── tests/                       # Pytest test suite (69 tests)
├── requirements.txt
└── LICENSE
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Start the API server
uvicorn backend.main:app --reload
```

The API documentation is available at `http://localhost:8000/docs` when the server is running.

## Privacy Safeguards

DRISHTI is **not** a surveillance system. It is a **humanitarian alert system**.

1. **Consent-First Database** — Only processes faces of registered missing persons.
2. **No Live Tracking** — Activates only on registered missing-person queries.
3. **Audit Trail** — Every search logged with officer ID; quarterly independent audit.
4. **Decentralised Architecture** — State police only sees their state data.
5. **Human-in-Loop** — AI flags, human decides. No automated detention.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.