# Developer setup

## Prerequisites

- Python 3.14
- Node.js 24 and npm
- Docker Desktop with Compose v2 for the packaged stack

## Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

The backend writes local data to `backend/data/citizen-karen.db`. Set `CITIZEN_KAREN_DB_PATH` to override it. API documentation is at <http://localhost:8000/api/docs>.

## Frontend

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. Vite proxies API calls to <http://localhost:8000>.

## Complete Docker stack

```bash
docker compose -f infra/docker-compose.yml up --build
```

The packaged app is at <http://localhost:8080>. Compose uses the network mock FCC connector and a named volume for SQLite.

## Environment

| Variable | Default | Purpose |
| --- | --- | --- |
| `CITIZEN_KAREN_DB_PATH` | `backend/data/citizen-karen.db` | SQLite file path |
| `CORS_ORIGINS` | local Vite origins | Comma-separated browser origins |
| `FCC_CONNECTOR_MODE` | `simulate` | `simulate` or `network` |
| `FCC_API_URL` | local mock endpoint | Endpoint used in network mode |

Never put production complaint data or credentials in `.env` files checked into Git.

## Quality commands

```bash
cd backend
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov=app --cov-fail-under=90

cd ../frontend
npm run lint
npm test
npm run build
npm audit --audit-level=high
```

From the repository root:

```bash
python -m pip install -r requirements-docs.txt
python -m mkdocs build --strict
docker compose -f infra/docker-compose.yml config --quiet
```

## Agency integrations

Only FCC is registered for direct submission. Add another connector only after completing the legal-risk, consent, data-minimization, failure-mode, accessibility, and test review in the [agency plugin guide](AGENCY_PLUGIN_GUIDE.md).
