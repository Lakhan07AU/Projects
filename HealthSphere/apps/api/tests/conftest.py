"""Shared pytest fixtures. Runs against an isolated SQLite database."""
import os
import pathlib
import time

import pytest

TEST_DB_PATH = pathlib.Path(__file__).parent / "test_healthsphere.db"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["SEED_DEMO"] = "0"
os.environ["AI_PROVIDER"] = "mock"
os.environ["TASK_QUEUE_MODE"] = "inline"
os.environ["LOCAL_STORAGE_PATH"] = str(TEST_DB_PATH.parent / "test_storage")

# Remove stale DB before collecting
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.clinical.seed_data import seed_clinical_knowledge  # noqa: E402
from app.clinical.specialist_data import seed_specialist_knowledge  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_rate_limiter():
    """Tests create many accounts from one IP; reset buckets between tests."""
    import app.core.rate_limit as rl

    rl.clear_rate_limits()
    yield


@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_clinical_knowledge(db)
        seed_specialist_knowledge(db)
    finally:
        db.close()

    from app.main import app

    with TestClient(app) as c:
        yield c

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def auth_headers(client, email: str, password: str = "Password123!"):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def wait_for_report(client, headers, report_id, timeout=15):
    """Inline processing runs in a background thread; poll until done."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.get(f"/api/v1/reports/{report_id}", headers=headers)
        status = resp.json()["report"]["status"]
        if status in ("complete", "failed"):
            return resp
        time.sleep(0.2)
    raise TimeoutError("Report processing did not finish in time")


def make_pdf(text_lines: list[str]) -> bytes:
    """Build a minimal valid single-page PDF containing the given lines."""
    lines = []
    for i, line in enumerate(text_lines):
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        lines.append(f"BT /F1 11 Tf 40 {750 - i * 16} Td ({escaped}) Tj ET")

    stream_content = "\n".join(lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream_content)).encode() + b" >>\nstream\n"
        + stream_content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for num, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{num} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF".encode()
    )
    return bytes(out)


SAMPLE_LAB_TEXT = [
    "Sunrise Diagnostics Laboratory",
    "Lab Report Date: 2026-08-20",
    "Patient Name: Demo Patient",
    "HbA1c  6.8 %   (Reference: 4.0 - 5.6 %)",
    "Total Cholesterol  230 mg/dL (Reference: 120 - 200 mg/dL)",
    "HDL Cholesterol 38 mg/dL (Reference: 40 - 60 mg/dL)",
    "TSH 2.1 uIU/mL (Reference: 0.4 - 4.0 uIU/mL)",
]
