"""Registration, login, JWT and role-based authorization tests."""
from __future__ import annotations


def test_register(client):
    resp = client.post("/api/auth/register", json={
        "name": "New Citizen", "email": "newuser@test.com",
        "phone": "9999999999", "password": "strongpass1",
    })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "CITIZEN"
    assert data["user"]["email"] == "newuser@test.com"
    assert "password" not in str(data)


def test_register_duplicate_email(client):
    resp = client.post("/api/auth/register", json={
        "name": "Dup", "email": "newuser@test.com", "password": "strongpass1",
    })
    assert resp.status_code == 400


def test_register_weak_password(client):
    resp = client.post("/api/auth/register", json={
        "name": "Weak", "email": "weak@test.com", "password": "short",
    })
    assert resp.status_code == 422


def test_login_success(client):
    resp = client.post("/api/auth/login", json={
        "email": "citizen@test.com", "password": "password123",
    })
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == "CITIZEN"


def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", json={
        "email": "citizen@test.com", "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_password_not_stored_plaintext(client):
    from app.db.database import SessionLocal
    from app.db.models import User

    db = SessionLocal()
    user = db.query(User).filter(User.email == "citizen@test.com").first()
    assert user.hashed_password != "password123"
    assert user.hashed_password.startswith("$2")
    db.close()


def test_me(client, tokens):
    resp = client.get("/api/auth/me", headers=auth(tokens["citizen"]))
    assert resp.status_code == 200
    assert resp.json()["email"] == "citizen@test.com"


def _register_and_login(client, email: str) -> str:
    resp = client.post("/api/auth/register", json={
        "name": "Fresh User", "email": email, "password": "initialpass1",
    })
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def test_update_profile(client):
    token = _register_and_login(client, "profile@test.com")
    resp = client.patch("/api/auth/me", json={"name": "Renamed User", "phone": "9876543210"},
                        headers=auth(token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed User"
    assert resp.json()["phone"] == "9876543210"


def test_change_password(client):
    token = _register_and_login(client, "pwchange@test.com")
    resp = client.post("/api/auth/me/password",
                       json={"current_password": "initialpass1", "new_password": "newpassword9"},
                       headers=auth(token))
    assert resp.status_code == 200

    resp = client.post("/api/auth/login", json={
        "email": "pwchange@test.com", "password": "newpassword9",
    })
    assert resp.status_code == 200


def test_change_password_wrong_current(client):
    token = _register_and_login(client, "pwwrong@test.com")
    resp = client.post("/api/auth/me/password",
                       json={"current_password": "wrongpass", "new_password": "whatever123"},
                       headers=auth(token))
    assert resp.status_code == 400


def test_me_unauthenticated(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_citizen_cannot_access_government_api(client, tokens):
    resp = client.get("/api/dashboard/statistics", headers=auth(tokens["citizen"]))
    assert resp.status_code == 403


def test_government_can_access_dashboard(client, tokens):
    resp = client.get("/api/dashboard/statistics", headers=auth(tokens["official"]))
    assert resp.status_code == 200


def test_only_admin_manages_cost_rates(client, tokens):
    resp = client.patch("/api/cost-rates/1", json={"value": 9999},
                        headers=auth(tokens["official"]))
    assert resp.status_code == 403

    from app.db.database import SessionLocal
    from app.db.models import CostRate
    db = SessionLocal()
    rate = db.query(CostRate).filter(CostRate.rate_key == "ASPHALT_PER_SQM").first()
    rate_id = rate.id
    db.close()
    resp = client.patch(f"/api/cost-rates/{rate_id}", json={"value": 3000},
                        headers=auth(tokens["admin"]))
    assert resp.status_code == 200
    assert resp.json()["value"] == 3000
    assert resp.json()["previous_value"] == 2200


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
