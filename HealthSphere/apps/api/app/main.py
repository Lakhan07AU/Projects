"""HealthSphere backend application entry point."""
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger("healthsphere")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.is_production:
        # Dev convenience: ensure tables exist even without running migrations.
        from app.core.database import Base, SessionLocal
        from app import models  # noqa: F401 — register models

        Base.metadata.create_all(bind=engine)
        from app.clinical.seed_data import seed_clinical_knowledge
        from app.clinical.specialist_data import seed_specialist_knowledge
        from app.services.seed import seed_demo_data_if_requested

        db = SessionLocal()
        try:
            seed_clinical_knowledge(db)
            seed_specialist_knowledge(db)
            seed_demo_data_if_requested(db)
        finally:
            db.close()
    yield


app = FastAPI(
    title="HealthSphere API",
    description=(
        "AI-powered personal & family health intelligence platform. "
        "Decision support only — never a substitute for professional medical advice."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---- Routers ----
from app.api.v1 import account, auth, care, family, intelligence, lifestyle, metrics, profile, reports, specialists

API = "/api/v1"
app.include_router(auth.router, prefix=API)
app.include_router(profile.router, prefix=API)
app.include_router(family.router, prefix=API)
app.include_router(reports.router, prefix=API)
app.include_router(metrics.router, prefix=API)
app.include_router(intelligence.router, prefix=API)
app.include_router(care.router, prefix=API)
app.include_router(specialists.router, prefix=API)
app.include_router(lifestyle.router, prefix=API)
app.include_router(account.router, prefix=API)


# ---- Observability ----
@app.get("/health", tags=["ops"])
def health():
    return {"status": "ok", "service": "healthsphere-api", "environment": settings.environment}


@app.get("/ready", tags=["ops"])
def ready():
    checks = {"database": False}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        logger.exception("Readiness: database check failed")
    return {
        "status": "ready" if all(checks.values()) else "degraded",
        "checks": checks,
        "ai_provider": settings.ai_provider,
        "queue_mode": settings.task_queue_mode,
    }
