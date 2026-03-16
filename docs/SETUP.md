# DRISHTI Development Setup Guide

## Quick Start (5 Minutes)

```bash
git clone https://github.com/atharva6969/DRISHTI.git
cd DRISHTI
cp .env.example .env
docker compose up --build
```

API docs: http://localhost:8000/docs  
Dashboard: http://localhost:3000

---

## Full Development Setup

### Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend |
| Node.js | 20+ | Frontend |
| PostgreSQL | 16+ | Production DB |
| Redis | 7+ | Task queue / cache |
| Docker | 24+ | Containerization |

### Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << 'EOF'
APP_ENV=development
DATABASE_URL=sqlite+aiosqlite:///./dev.db
REDIS_URL=redis://localhost:6379/0
APP_SECRET_KEY=dev-only-change-in-production
JWT_SECRET_KEY=dev-jwt-change-in-production
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=DEBUG
EOF

# Start development server (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Lint
ruff check app/ ml/
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
REACT_APP_API_URL=http://localhost:8000/api/v1 npm start

# Build for production
npm run build

# Run tests
npm test
```

### Community App Setup

```bash
cd community-app
npm install
npm start
```

---

## Project Structure

```
DRISHTI/
├── backend/
│   ├── app/                    # FastAPI application
│   │   ├── main.py             # Application entry point
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── api/v1/             # API endpoints
│   │   │   └── endpoints/      # auth, cases, search, alerts, sightings, community
│   │   ├── core/               # Database, security, deps, logging
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic
│   │   └── utils/              # Helpers
│   ├── ml/                     # AI/ML engines
│   │   ├── face_recognition/   # DeepFace + ArcFace
│   │   ├── gait_recognition/   # OpenGait integration
│   │   ├── clothing_detection/ # CLIP-based clothing fingerprint
│   │   ├── body_biometrics/    # MediaPipe Pose metrics
│   │   ├── route_predictor/    # NetworkX trafficking route predictor
│   │   ├── age_progression/    # SAM-Age integration
│   │   └── multimodal_engine.py # Combined identity engine
│   ├── tests/                  # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Router setup
│   │   ├── store.ts            # Redux store
│   │   ├── slices/             # Redux state slices
│   │   ├── pages/              # Dashboard, Cases, Search, Alerts, Map, Community
│   │   ├── components/         # Reusable UI components
│   │   ├── services/api.ts     # Axios API client
│   │   └── styles/global.css   # Global CSS variables
│   └── package.json
├── community-app/              # WhatsApp bot UI
├── edge-deployment/            # TFLite edge inference
├── kubernetes/                 # K8s manifests
├── docs/                       # Documentation
├── docker-compose.yml
├── .env.example
└── .github/workflows/ci.yml    # CI/CD pipeline
```

---

## Creating a Test Officer Account

```python
# Run in Python console with backend running
import asyncio, httpx

async def create_officer():
    async with httpx.AsyncClient() as c:
        r = await c.post("http://localhost:8000/api/v1/auth/register", json={
            "badge_number": "TEST-001",
            "full_name": "Test Officer",
            "email": "test@example.com",
            "password": "Test@12345",
            "role": "officer",
            "station": "Test Station"
        })
        print(r.json())

asyncio.run(create_officer())
```

---

## Running Individual ML Engines

```python
# Face Recognition
from ml.face_recognition.engine import FaceRecognitionEngine
engine = FaceRecognitionEngine()
result = engine.extract_embedding(open("photo.jpg", "rb").read())
print(f"Embedding: {result.embedding[:5]}...")

# Route Predictor
from ml.route_predictor.predictor import TraffickingRoutePredictor
predictor = TraffickingRoutePredictor()
activation = predictor.predict_routes(
    case_id=1, case_number="DRISHTI-20240101-AABBCC",
    source_location="Murshidabad", age=16, gender="female",
    case_type="trafficking"
)
for route in activation.predicted_routes:
    print(f"Route: {' → '.join(route.path)} | Probability: {route.probability:.0%}")
```
