Team Booking Calendar -> https://calendar.app.google/Wt3PZsR2sbzLsZKCA 
# Citizen Karen™ — Unified Government Complaint Platform

Citizen Karen is a plugin-based platform that lets citizens submit complaints
(FCC, IRS, CFPB, state agencies, etc.) through a single portal and API.

## Monorepo Layout

- `backend/` – FastAPI + plugin engine
- `frontend/` – React SPA for citizens + admins
- `api/` – OpenAPI spec + shared schemas
- `docs/` – BRD/TRD, roadmap, pricing, integration guides
- `infra/` – Docker Compose, K8s manifests, monitoring
- `branding/` – Logos, color palettes, design assets

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
