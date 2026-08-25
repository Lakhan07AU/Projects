"""Authentication flow tests."""
from tests.conftest import auth_headers


def test_register_login_me(client):
    headers = auth_headers(client, "auth1@example.com")

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "auth1@example.com"

    # login
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "auth1@example.com", "password": "Password123!"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"] and tokens["refresh_token"]


def test_wrong_password_rejected(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "auth1@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 403


def test_duplicate_email_rejected(client):
    auth_headers(client, "auth2@example.com")
    dup = client.post(
        "/api/v1/auth/register",
        json={"email": "auth2@example.com", "password": "Password123!", "full_name": "X"},
    )
    assert dup.status_code == 409


def test_short_password_rejected(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "shortpw@example.com", "password": "short", "full_name": "X"},
    )
    assert resp.status_code == 422


def test_refresh_rotation_and_logout(client):
    headers = auth_headers(client, "auth3@example.com")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "auth3@example.com", "password": "Password123!"},
    ).json()
    old_refresh = login["refresh_token"]

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refreshed.status_code == 200
    new_tokens = refreshed.json()

    # Old refresh token must be revoked (rotation)
    reuse = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse.status_code == 403

    # Logout revokes the new refresh token
    out = client.post(
        "/api/v1/auth/logout", json={"refresh_token": new_tokens["refresh_token"]}, headers=headers
    )
    assert out.status_code == 200
    revoked = client.post("/api/v1/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]})
    assert revoked.status_code == 403


def test_access_token_required(client):
    resp = client.get("/api/v1/reports")
    assert resp.status_code == 403  # no credentials

    bad = client.get("/api/v1/reports", headers={"Authorization": "Bearer garbage.token.here"})
    assert bad.status_code == 403
