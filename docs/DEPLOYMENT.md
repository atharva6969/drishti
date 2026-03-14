# DRISHTI Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose 2+
- 4 CPU / 8 GB RAM minimum
- PostgreSQL 16+ (managed or container)
- Redis 7+ (managed or container)

---

## 1. Local Development (Docker Compose)

```bash
# Clone the repository
git clone https://github.com/atharva6969/DRISHTI.git
cd DRISHTI

# Copy environment template
cp .env.example .env
# Edit .env with your values

# Start all services
docker compose up --build

# The following will be available:
#   Backend API:   http://localhost:8000
#   API Docs:      http://localhost:8000/docs
#   Frontend:      http://localhost:3000
#   PostgreSQL:    localhost:5432
#   Redis:         localhost:6379
```

---

## 2. Manual Development Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment
export DATABASE_URL="sqlite+aiosqlite:///./dev.db"
export SECRET_KEY="dev-secret-key"
export APP_SECRET_KEY="dev-secret-key"
export JWT_SECRET_KEY="dev-jwt-key"
export ENVIRONMENT="development"

# Run migrations (create tables on first start)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000/api/v1 npm start
```

### Run Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov=ml
```

---

## 3. Kubernetes Production Deployment

### Prerequisites

- Kubernetes cluster (EKS/GKE/AKS)
- `kubectl` configured
- `helm` installed (for cert-manager, nginx-ingress)

### Steps

```bash
# 1. Create namespace
kubectl apply -f kubernetes/configmap.yaml

# 2. Create secrets (edit kubernetes/secret.yaml first!)
kubectl apply -f kubernetes/secret.yaml

# 3. Deploy services
kubectl apply -f kubernetes/service.yaml

# 4. Deploy applications
kubectl apply -f kubernetes/deployment.yaml

# 5. Verify
kubectl get pods -n drishti
kubectl get svc -n drishti

# 6. Check logs
kubectl logs -n drishti -l app=drishti,component=backend
```

### Environment Variables for Production

Set these in the Kubernetes secret (not configmap):
- `SECRET_KEY` — long random string (64+ chars)
- `JWT_SECRET_KEY` — separate long random string
- `DATABASE_URL` — production PostgreSQL URL
- `REDIS_URL` — production Redis URL
- `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` — for WhatsApp/SMS
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` — for S3 evidence storage

---

## 4. ML Model Setup

### Face Recognition (DeepFace + ArcFace)
```bash
pip install deepface tensorflow
# Models download automatically on first use (~200MB)
```

### Gait Recognition (OpenGait)
```bash
# Clone OpenGait
git clone https://github.com/ShiqiYu/OpenGait.git backend/ml/models/opengait
cd backend/ml/models/opengait
pip install -r requirements.txt
# Download pretrained GaitSet weights:
# https://github.com/ShiqiYu/OpenGait/releases
```

### Clothing Detection (CLIP)
```bash
pip install open-clip-torch
# Model downloads automatically on first use (~340MB)
```

### Body Biometrics (MediaPipe)
```bash
pip install mediapipe
# Pose model downloads automatically (~6MB)
```

### Age Progression (SAM-Age)
```bash
# Install SAM dependencies
pip install torch torchvision
git clone https://github.com/yuval-alaluf/SAM.git backend/ml/models/sam
# Download pretrained weights from the SAM repository
```

### Route Predictor
```bash
pip install networkx xgboost
# Route database is built-in — no model download required
```

---

## 5. Monitoring & Observability

### Health Checks
```bash
# Liveness
curl http://localhost:8000/health

# Readiness
curl http://localhost:8000/ready
```

### Logs
```bash
# Docker Compose
docker compose logs -f backend

# Kubernetes
kubectl logs -n drishti -l component=backend -f
```

---

## 6. Database Migrations

The database schema is created automatically via SQLAlchemy metadata on startup.
For production schema changes, use Alembic:

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```
