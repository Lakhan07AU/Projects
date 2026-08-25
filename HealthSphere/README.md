# HealthSphere

A personal health-record web application with a **privacy-first, safety-first** design:
you own your data, the AI never diagnoses, and every automated insight is traceable to a
validated public-health source.

## What it does

| Area | Features |
|---|---|
| **Records** | Upload lab reports (PDF/image), background extraction of values into structured metrics, original file preserved and downloadable |
| **Health graph** | Manual + report-sourced measurements, trend charts with direction/stability/outlier flags |
| **Timeline** | Every event (reports, measurements, guidance, family history) in one chronological view |
| **Insights engine** | Deterministic rules from validated guidelines (WHO/CDC/IAP style) produce *preventive-care discussion topics* — never diagnoses — each citing its rule source |
| **Family history** | Relative-level conditions feed risk-topic rules |
| **Lifestyle** | Weekly movement plan, nutrition swaps, exercise/sleep logging — clearly separated from medical care |
| **Assistant** | General health-education chat with hard refusals for diagnosis/dosage/report interpretation, emergency-keyword escalation, cited sources, per-user rate limits |
| **Find care** | Doctor & hospital directory (mock data in this build) |
| **Emergency SOS** | One-tap alert to saved contacts with a medical card (blood type, allergies, conditions); explicit "call local services first" messaging |
| **Privacy** | Granular consent toggles, full JSON export job, permanent one-click deletion |

## Architecture

```
┌───────────────────┐        ┌───────────────────────────────────────────┐
│  Next.js 15 web   │  HTTP  │  FastAPI (apps/api)                        │
│  Tailwind, RQ     │ ─────► │  /api/v1: auth, profile, family, reports,  │
│  TanStack Query   │  JWT   │  metrics, timeline, insights, lifestyle,   │
└───────────────────┘        │  assistant, care, emergency, privacy       │
                             └──────┬────────────────┬─────────────────────┘
                                    │                │
                          ┌─────────▼─────┐   ┌──────▼──────┐
                          │ PostgreSQL /  │   │ Redis       │
                          │ SQLite (dev)  │   │ (Celery or  │
                          └───────────────┘   │ inline mode)│
                                              └─────────────┘
```

- **Backend**: `apps/api` — FastAPI + SQLAlchemy 2.0 + Alembic; Celery worker for report
  processing (`TASK_QUEUE_MODE=inline` runs jobs in-process for simple local dev).
- **Frontend**: `apps/web` — Next.js App Router, TypeScript, Tailwind, Recharts-style SVG charts.
- **AI layer**: pluggable provider (`app/ai/providers/`) — `mock` by default, optional OpenAI-compatible endpoint. The assistant prompt enforces scope; extraction failures are surfaced honestly.

## Safety design (non-negotiables)

1. **No diagnosis, ever.** Insights are framed as topics to discuss with a professional.
2. **Traceability.** Every insight links to its rule/knowledge source key shown in the UI.
3. **Honest failure.** If a document can't be parsed, the app says so instead of guessing.
4. **Assistant guardrails.** Refuses diagnosis/dosage/personal-report interpretation;
   detects emergency language and directs to local emergency numbers.
5. **Data ownership.** Consent toggles, full export, irreversible delete — all user-initiated.
6. **Audit trail.** Sensitive actions are logged.

## Quick start (no Docker)

```bash
# 1. Backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (source .venv/bin/activate on Unix)
pip install -r apps/api/requirements.txt
copy .env.example .env            # defaults use SQLite + inline queue + mock AI
cd apps/api && alembic upgrade head && cd ../..
uvicorn app.main:app --reload --app-dir apps/api    # → http://localhost:8000/docs

# 2. Frontend
cd apps/web
npm install
npm run dev                       # → http://localhost:3000
```

## Quick start (Docker)

```bash
docker compose up --build
# web      → http://localhost:3000
# api docs → http://localhost:8000/docs
# worker   → celery report-processing container (shares the uploads volume)
```

## Tests

```bash
.venv\Scripts\python.exe -m pytest apps\api\tests -q     # 30 tests: auth, security/isolation,
                                                          # clinical rules, trends, integration
cd apps/web && npm run build                              # strict type-check of all routes
```

## Configuration

See `.env.example`. Notable switches:
- `DATABASE_URL` — Postgres in Docker, SQLite for zero-setup dev
- `TASK_QUEUE_MODE` — `inline` (no Redis needed) vs `celery`
- `AI_PROVIDER` — `mock` deterministic extractor/chat, or any OpenAI-compatible API

> **Disclaimer** — This project is an educational build. It is not a medical device and does
> not provide medical advice. Always consult qualified healthcare professionals.
