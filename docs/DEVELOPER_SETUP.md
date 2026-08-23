# Developer Setup Guide

This guide walks you through setting up the Citizen Karen platform for local development, running it with Docker, executing the test suites, and understanding the repository structure.

---

## Prerequisites

| Tool | Minimum Version | Notes |
|------|----------------|-------|
| Python | 3.11 | Required for the backend |
| Node.js | 20 | Required for the frontend |
| npm | 9+ | Bundled with Node.js 20 |
| Docker | 24+ | Required for the Docker workflow |
| Docker Compose | v2 (plugin) | Ships with Docker Desktop |
| Git | 2.40+ | |

---

## Repository Structure

```text
citizen-karen-platform/
├── backend/                # FastAPI backend + agency plugin engine
│   ├── app/
│   │   ├── plugins/        # Agency-specific submission plugins
│   │   │   ├── base.py         # Plugin base class
│   │   │   ├── registry.py     # Plugin registry
│   │   │   ├── fcc_plugin.py   # FCC agency plugin
│   │   │   └── sample_agency.py
│   │   ├── complaints.py   # Complaint routes & logic
│   │   ├── db.py           # Database helpers
│   │   ├── logging_config.py
│   │   ├── metrics.py      # Prometheus metrics
│   │   └── main.py         # FastAPI application entry point
│   ├── tests/              # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React SPA (citizen + admin views)
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── index.css
│   ├── package.json
│   └── Dockerfile (if present)
├── api/                    # OpenAPI 3.1 spec + shared schemas
│   ├── openapi.yaml
│   └── schemas/
│       └── complaint.schema.json
├── docs/                   # Project documentation (MkDocs)
├── infra/                  # Docker Compose, Kubernetes manifests
│   ├── docker-compose.yml
│   └── Dockerfile.backend
├── branding/               # Logos, fonts, color palette
├── mkdocs.yml              # MkDocs configuration
└── README.md
```

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Lipford-Dutch/citizen-karen-platform.git
cd citizen-karen-platform
```

### 2. Backend

#### Create and activate a virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows PowerShell
```

#### Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-cov     # development/testing extras
```

#### Run the backend server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at <http://localhost:8000>.  
Interactive docs: <http://localhost:8000/docs>  
Health check: <http://localhost:8000/health>

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

The development server will open the app in your browser at <http://localhost:3000> (or the port Webpack prints).

---

## Docker Setup

The `infra/` directory contains a Docker Compose file that builds and starts the backend (and any dependent services).

```bash
# From the repository root
docker compose -f infra/docker-compose.yml up --build
```

| Service | URL |
|---------|-----|
| backend | <http://localhost:8000> |

To stop all services:

```bash
docker compose -f infra/docker-compose.yml down
```

To rebuild without cache after dependency changes:

```bash
docker compose -f infra/docker-compose.yml build --no-cache
docker compose -f infra/docker-compose.yml up
```

---

## Running the Test Suites

### Backend (pytest)

```bash
cd backend
pytest --cov=./ --cov-report=term-missing
```

To run a single test file:

```bash
pytest -q tests/test_health.py
```

Coverage reports are generated as `coverage.xml` (consumed by CI) and printed to the terminal.

### Frontend (Jest + React Testing Library)

```bash
cd frontend
npm test -- --watchAll=false
```

### Linting & Formatting

**Backend:**

```bash
cd backend
pip install flake8 black isort
black --check .
isort --check-only .
flake8 .
```

To auto-fix formatting:

```bash
black .
isort .
```

**Frontend:**

```bash
cd frontend
npm run lint
```

---

## Environment Variables

No `.env` file is required for local development with the default configuration. The following variables are supported:

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONUNBUFFERED` | `1` | Recommended in Docker for log streaming |
| `FCC_API_URL` | (set by plugin) | Override the FCC mock/real endpoint |

Create a `.env` file (git-ignored) at the repository root or `backend/` and export the relevant variables before starting the server.

---

## Adding a New Agency Plugin

1. Create `backend/app/plugins/<agency>_plugin.py` implementing the `BasePlugin` interface from `base.py`.
2. Register the plugin in `backend/app/plugins/registry.py`.
3. Add corresponding tests under `backend/tests/`.

See [AGENCY_PLUGIN_GUIDE.md](AGENCY_PLUGIN_GUIDE.md) for the full plugin authoring guide.

---

## Continuous Integration

CI runs automatically on push to `main` and all `feature/**` / `bugfix/**` branches via GitHub Actions:

| Job | Command |
|-----|---------|
| Backend tests | `pytest --cov=./ --cov-report=xml` (from `backend/`) |
| Frontend tests | `npm test -- --ci --coverage` (from `frontend/`) |
| Backend lint | `black --check`, `isort --check-only`, `flake8` |
| Frontend lint | `npm run lint` |

See `.github/workflows/tests.yml` for the full workflow definition.
