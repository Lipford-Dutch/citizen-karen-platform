Grafana Cloud - https://karingusa01.grafana.net/a/grafana-setupguide-app/home

Team Booking Calendar -> https://calendar.app.google/Wt3PZsR2sbzLsZKCA 
# Citizen Karen™ — Unified Government Complaint Platform

Citizen Karen is a plugin-based platform that lets citizens submit complaints
(FCC, IRS, CFPB, state agencies, etc.) through a single portal and API.

## Monorepo Layout

karing-usa/
├── backend/                # FastAPI + agency plugin engine
│   └── app/
│       ├── api/
│       ├── plugins/
│       ├── models.py
│       ├── db.py
│       ├── logging_config.py
│       ├── metrics.py
│       └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React SPA for citizen + admin views
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── index.css
│   ├── package.json
│   └── Dockerfile
├── api/                    # OpenAPI 3.1 spec + shared schemas
│   ├── openapi.yaml
│   └── schemas/
│       └── complaint.schema.json
├── docs/                   # Docs: BRD, TRD, guides, roadmap
│   ├── business-requirements.md
│   ├── technical-architecture.md
│   ├── integration-guide.md
│   ├── roadmap.md
│   └── pricing.md
├── infra/                  # Infra as Code: Docker Compose, K8s, monitoring
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── k8s/
│       ├── frontend.yaml
│       ├── backend.yaml
│       └── postgres.yaml
├── branding/               # Logos, fonts, palettes, Figma exports
│   ├── logo.svg
│   ├── favicon.ico
│   ├── brand-colors.md
│   └── design-system.fig
└── README.md


## Quick Start (Dev)

```bash
# Backend (FastAPI)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (later)
cd frontend
npm install
npm start

API will be available at: http://localhost:8000
OpenAPI docs: http://localhost:8000/docs
