# 🏛️ Citizen Karen™ — Unified Government Complaint Platform

Citizen Karen is a plugin-based platform that lets citizens submit complaints (FCC, IRS, CFPB, state agencies, etc.) through a **single portal and API**.

## 🔗 Important Links

* **Grafana Cloud (Monitoring/Metrics):** [https://karingusa01.grafana.net/a/grafana-setupguide-app/home](https://karingusa01.grafana.net/a/grafana-setupguide-app/home)
* **Team Booking Calendar:** [https://calendar.app.google/Wt3PZsR2sbzLsZKCA](https://calendar.app.google/Wt3PZsR2sbzLsZKCA)

---

## 🏗️ Monorepo Layout

The repository uses a monorepo structure, organized as follows:

```text
karing-usa/
├── backend/                # FastAPI + agency plugin engine
│   ├── app/
│   │   ├── api/
│   │   ├── plugins/
│   │   ├── models.py
│   │   ├── db.py
│   │   ├── logging_config.py
│   │   ├── metrics.py
│   │   └── main.py
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
