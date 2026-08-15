"""Tests for public endpoints, admin user listing and page serving."""
from __future__ import annotations


def test_public_stats(client):
    resp = client.get("/api/public/stats")
    assert resp.status_code == 200
    data = resp.json()
    # Flow tests may add extra potholes during the session, so only assert lower bounds.
    assert data["total_potholes"] >= 10
    assert data["repaired"] >= 0
    assert data["repair_completion_rate"] >= 0


def test_public_recent(client):
    resp = client.get("/api/public/recent?limit=4")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) <= 4
    for r in rows:
        assert "code" in r and "severity" in r and "status" in r


def test_map_potholes_geojson(client):
    resp = client.get("/api/map/potholes?severity=CRITICAL")
    assert resp.status_code == 200
    fc = resp.json()
    assert fc["type"] == "FeatureCollection"
    for f in fc["features"]:
        assert f["geometry"]["type"] == "Point"
        assert f["properties"]["severity"] == "CRITICAL"


def test_admin_users_listing(client, tokens):
    resp = client.get("/api/users", headers=auth(tokens["admin"]))
    assert resp.status_code == 200
    emails = [u["email"] for u in resp.json()]
    assert "citizen@test.com" in emails


def test_users_listing_forbidden_for_official(client, tokens):
    resp = client.get("/api/users", headers=auth(tokens["official"]))
    assert resp.status_code == 403


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["demo_mode"] is True


def test_page_serving(client):
    assert client.get("/").status_code == 200
    assert client.get("/login").status_code == 200
    assert client.get("/index.html").status_code == 200
    css = client.get("/css/style.css")
    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
