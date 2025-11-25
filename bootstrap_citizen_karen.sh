#!/usr/bin/env bash
set -e

echo "Bootstrapping Citizen Karen monorepo structure..."

# Root files and directories
mkdir -p .github/workflows
mkdir -p docs diagrams api/backend_schemas
mkdir -p backend/app/{core,api/v1,models,services,plugins,db,migrations,utils}
mkdir -p backend/tests/{unit,integration}
mkdir -p frontend/src/{components,pages,services,theme}
mkdir -p frontend/tests
mkdir -p infra/{k8s,monitoring,mock-agencies}
mkdir -p branding

################################
# Root: README & .gitignore
################################

cat > README.md << 'EOF'
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

## Quick Start (Backend Dev)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

