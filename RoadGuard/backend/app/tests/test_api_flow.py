"""End-to-end API flow tests: image analysis, complaint submission, duplicate
detection, repair workflow and notifications."""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image


def _demo_image(width=640, height=480, dark_pixels=True) -> bytes:
    img = Image.new("RGB", (width, height), (80, 80, 80))
    if dark_pixels:
        for y in range(100, 200):
            for x in range(200, 320):
                img.putpixel((x, y), (20, 20, 20))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _analyze(client, token, content=None):
    content = content or _demo_image()
    return client.post(
        "/api/reports/analyze",
        files={"file": ("pothole.jpg", content, "image/jpeg")},
        headers=_headers(token),
    )


# ---------- Image validation ----------

def test_analyze_rejects_invalid_file(client, tokens):
    resp = client.post(
        "/api/reports/analyze",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
        headers=_headers(tokens["citizen"]),
    )
    assert resp.status_code == 400


def test_analyze_rejects_oversized_file(client, tokens):
    # Over 15 MB limit
    resp = client.post(
        "/api/reports/analyze",
        files={"file": ("big.jpg", b"\x00" * (16 * 1024 * 1024), "image/jpeg")},
        headers=_headers(tokens["citizen"]),
    )
    assert resp.status_code == 400


def test_analyze_requires_auth(client):
    resp = client.post("/api/reports/analyze",
                       files={"file": ("p.jpg", _demo_image(), "image/jpeg")})
    assert resp.status_code == 401


def test_analyze_detects_pothole_demo(client, tokens):
    resp = _analyze(client, tokens["citizen"])
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["demo_mode"] is True
    assert data["detected"] in (True, False)
    assert 0 <= data["severity_score"] <= 100
    assert data["estimated_area"] >= 0
    assert data["repair_cost_breakdown"]["total"] == data["estimated_cost"]


# ---------- Complaint submission + duplicate detection ----------

def test_full_complaint_flow(client, tokens):
    resp = _analyze(client, tokens["citizen"])
    assert resp.status_code == 200

    submit = client.post(
        "/api/reports",
        json={
            "latitude": 28.6139,
            "longitude": 77.2090,
            "city": "Cityville",
            "district": "Demo District",
            "state": "Demo State",
            "ward": "1",
            "road": "MG Road",
        },
        headers=_headers(tokens["citizen"]),
    )
    assert submit.status_code == 201, submit.text
    data = submit.json()
    assert data["report"]["report_code"].startswith("RGA-")
    assert data["pothole"]["pothole_code"].startswith("PTH-")
    assert data["pothole"]["status"] == "PENDING_VERIFICATION"


def test_duplicate_detection_attaches_to_existing(client, tokens):
    # First report at a location
    _analyze(client, tokens["citizen"])
    first = client.post(
        "/api/reports",
        json={"latitude": 28.6100, "longitude": 77.2100, "ward": "2", "road": "Station Road"},
        headers=_headers(tokens["citizen"]),
    ).json()
    pothole_id = first["pothole"]["id"]

    # Second report very close -> should attach as duplicate
    _analyze(client, tokens["citizen"])
    second = client.post(
        "/api/reports",
        json={"latitude": 28.61001, "longitude": 77.21001, "ward": "2", "road": "Station Road"},
        headers=_headers(tokens["citizen"]),
    )
    assert second.status_code == 201, second.text
    data = second.json()
    assert data["duplicate"] is True
    assert data["pothole"]["id"] == pothole_id
    assert data["report"]["duplicate_of"] == pothole_id


def test_far_away_report_not_duplicate(client, tokens):
    _analyze(client, tokens["citizen"])
    far = client.post(
        "/api/reports",
        json={"latitude": 19.0760, "longitude": 72.8777, "ward": "1", "road": "MG Road"},
        headers=_headers(tokens["citizen"]),
    )
    assert far.status_code == 201
    assert far.json()["duplicate"] is False


# ---------- Repair workflow ----------

def test_government_verify_assign_repair_complete(client, tokens):
    # Build a pothole in PENDING_VERIFICATION via citizen report
    _analyze(client, tokens["citizen"])
    submit = client.post(
        "/api/reports",
        json={"latitude": 28.6150, "longitude": 77.2110, "ward": "3", "road": "College Road"},
        headers=_headers(tokens["citizen"]),
    ).json()
    pid = submit["pothole"]["id"]

    # Government verifies
    r = client.post(f"/api/potholes/{pid}/verify", json={"action": "verify"},
                    headers=_headers(tokens["official"]))
    assert r.status_code == 200
    assert r.json()["status"] == "VERIFIED"

    # Citizen cannot verify
    r = client.post(f"/api/potholes/{pid}/verify", json={"action": "verify"},
                    headers=_headers(tokens["citizen"]))
    assert r.status_code == 403

    # Government prioritizes then assigns to team 1
    r = client.post(f"/api/potholes/{pid}/prioritize",
                    json={"priority": "CRITICAL", "priority_score": 92, "reason": "test"},
                    headers=_headers(tokens["official"]))
    assert r.status_code == 200
    assert r.json()["priority"] == "CRITICAL"

    r = client.patch(f"/api/potholes/{pid}/status", json={"status": "PRIORITIZED"},
                     headers=_headers(tokens["official"]))
    assert r.status_code == 200

    r = client.post(f"/api/potholes/{pid}/assign", json={"team_id": 1, "deadline_days": 5},
                    headers=_headers(tokens["official"]))
    assert r.status_code == 200
    assert r.json()["status"] == "ASSIGNED"

    # Repair team starts work
    repairs = client.get("/api/repairs", headers=_headers(tokens["team"])).json()
    repair_id = next(x["id"] for x in repairs if x["pothole_id"] == pid)

    r = client.post(f"/api/repairs/{repair_id}/start", headers=_headers(tokens["team"]))
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"

    # Progress update with image
    r = client.post(f"/api/repairs/{repair_id}/progress", headers=_headers(tokens["team"]),
                    data={"note": "Patch applied"}, files={"file": ("p.jpg", _demo_image(), "image/jpeg")})
    assert r.status_code == 200

    # Complete with actual cost
    r = client.post(f"/api/repairs/{repair_id}/complete",
                    data={"actual_cost": "25000", "note": "Done"},
                    headers=_headers(tokens["team"]))
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "COMPLETED"
    assert r.json()["actual_cost"] == 25000

    # Invalid transition blocked: COMPLETED -> VERIFIED (must be CITIZEN_VERIFICATION)
    r = client.patch(f"/api/potholes/{pid}/status", json={"status": "VERIFIED"},
                     headers=_headers(tokens["official"]))
    assert r.status_code == 400

    # Government AI verify (before/after)
    r = client.post(f"/api/repairs/{repair_id}/verify", headers=_headers(tokens["official"]),
                    files={"file": ("after.jpg", _demo_image(dark_pixels=False), "image/jpeg")})
    assert r.status_code == 200
    assert 0 <= r.json()["verification_score"] <= 100
    assert "AI-assisted" in r.json()["label"]


# ---------- Dashboard ----------

def test_dashboard_statistics_and_analytics(client, tokens):
    r = client.get("/api/dashboard/statistics", headers=_headers(tokens["official"]))
    assert r.status_code == 200
    data = r.json()
    assert data["total_potholes"] >= 1
    assert len(data["cards"]) == 8

    r = client.get("/api/dashboard/analytics", headers=_headers(tokens["official"]))
    assert r.status_code == 200
    data = r.json()
    assert "severity" in data and "by_ward" in data
    assert data["pending_vs_completed"]["completed"] >= 0


def test_map_geojson(client):
    r = client.get("/api/map/potholes")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 1
    props = data["features"][0]["properties"]
    assert "code" in props and "severity" in props
    assert "phone" not in props and "email" not in props
