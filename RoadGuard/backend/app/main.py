"""RoadGuard AI - FastAPI application entry point."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    admin,
    ai,
    auth,
    dashboard,
    map as map_api,
    notifications,
    pages,
    potholes,
    repairs,
    reports,
)
from app.core.config import get_settings
from app.db.database import engine, init_db
from app.utils.logging import get_logger, log_request, setup_logging

settings = get_settings()
setup_logging()
logger = get_logger("roadguard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    (settings.storage_path / "potholes").mkdir(parents=True, exist_ok=True)
    (settings.storage_path / "repairs").mkdir(parents=True, exist_ok=True)
    (settings.storage_path / "profiles").mkdir(parents=True, exist_ok=True)
    logger.info("RoadGuard AI started (demo_mode=%s)", settings.DEMO_MODE)
    yield


app = FastAPI(
    title="RoadGuard AI",
    description=(
        "AI-powered pothole detection, automatic complaint registration, "
        "repair estimation and government management platform."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(potholes.router)
app.include_router(repairs.router)
app.include_router(dashboard.router)
app.include_router(map_api.router)
app.include_router(map_api.public_router)
app.include_router(ai.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:  # noqa: BLE001
        log_request(logger, request, 500, (time.perf_counter() - start) * 1000)
        raise exc
    log_request(logger, request, response.status_code, (time.perf_counter() - start) * 1000)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "app": settings.APP_NAME, "demo_mode": settings.DEMO_MODE}


@app.get("/", include_in_schema=False)
def root():
    return {"message": "RoadGuard AI API. See /docs for OpenAPI documentation."}


# Serve uploaded files.
uploads_dir = Path(settings.storage_path)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Keep the page/static catch-all LAST so API + upload routes are matched first.
app.include_router(pages.router)
