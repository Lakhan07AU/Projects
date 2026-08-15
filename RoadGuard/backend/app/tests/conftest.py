"""Pytest fixtures.

Sets a temporary SQLite database and temp storage before any app import so
tests never touch the development database.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

_TMPDIR = Path(tempfile.mkdtemp(prefix="roadguard_test_"))
os.environ["DATABASE_URL"] = f"sqlite:///{_TMPDIR / 'test.db'}"
os.environ["STORAGE_PATH"] = str(_TMPDIR / "uploads")
os.environ["DEMO_MODE"] = "true"
os.environ["JWT_SECRET"] = "test-secret"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.seed_data import SEED_COST_RATES  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def prepare_db():
    from app.db.database import SessionLocal, init_db
    from app.core.enums import Role
    from app.core.security import hash_password
    from app.db.models import CostRate, RepairTeam, User

    init_db()
    db = SessionLocal()
    try:
        for cr in SEED_COST_RATES:
            db.add(CostRate(
                rate_key=cr["rate_key"], name=cr["name"], unit=cr["unit"], value=cr["value"],
                description=cr["description"]))
        teams = {}
        for team in [
            {"name": "Team Alpha", "contact": "1", "manager_name": "M1", "city": "C", "ward": "1"},
            {"name": "Team Beta", "contact": "2", "manager_name": "M2", "city": "C", "ward": "2"},
        ]:
            t = RepairTeam(**team)
            db.add(t)
            db.flush()
            teams[t.name] = t
        for u in [
            ("citizen@test.com", "CITIZEN"), ("official@test.com", "GOVERNMENT_OFFICIAL"),
            ("admin@test.com", "ADMIN"), ("Team Alpha", "REPAIR_TEAM"),
        ]:
            db.add(User(
                name=u[0], email=u[0] if u[0] != "Team Alpha" else "repair@test.com",
                hashed_password=hash_password("password123"),
                role=Role(u[1])))
        # A small set of potholes + repairs so dashboard/map tests have data.
        from datetime import datetime, timedelta
        from app.db.models import Pothole, Repair
        for i in range(10):
            p = Pothole(
                pothole_code=f"PTH-{100000 + i}", latitude=28.60 + i * 0.001,
                longitude=77.20 + i * 0.001, city="Testcity", district="Test",
                state="Test", ward=str(1 + i % 3), road=f"Road {i % 3}",
                severity=("CRITICAL" if i % 5 == 0 else "HIGH" if i % 3 == 0 else "MEDIUM"),
                severity_score=40 + i, confidence=0.9, estimated_area=1 + i * 0.5,
                repair_area=1.2 + i * 0.5, estimated_cost=20000 + i * 1000,
                status="PENDING_VERIFICATION", report_count=1,
                created_at=datetime.utcnow() - timedelta(days=i))
            db.add(p)
            db.flush()
            if i < 3:
                db.add(Repair(
                    pothole_id=p.id, team_id=teams["Team Alpha"].id, estimated_cost=p.estimated_cost,
                    repair_area=p.repair_area, status="COMPLETED", actual_cost=p.estimated_cost * 1.1,
                    assigned_at=datetime.utcnow() - timedelta(days=10),
                    completion_date=datetime.utcnow() - timedelta(days=2)))
        db.commit()
    finally:
        db.close()
    yield
    shutil.rmtree(_TMPDIR, ignore_errors=True)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def tokens(client):
    """Return login tokens for every demo role."""
    out = {}
    for role, email in [
        ("citizen", "citizen@test.com"), ("official", "official@test.com"),
        ("admin", "admin@test.com"), ("team", "repair@test.com"),
    ]:
        resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
        assert resp.status_code == 200, resp.text
        out[role] = resp.json()["access_token"]
    return out


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
