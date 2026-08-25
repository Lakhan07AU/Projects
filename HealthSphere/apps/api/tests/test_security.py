"""Object-level authorization (BOLA) and security tests."""
from tests.conftest import auth_headers, make_pdf


def test_user_a_cannot_read_user_b_report(client):
    headers_a = auth_headers(client, "sec-a@example.com")
    headers_b = auth_headers(client, "sec-b@example.com")

    pdf = make_pdf(["HbA1c 5.4 %"])
    upload = client.post(
        "/api/v1/reports?category=hba1c",
        files={"file": ("report.pdf", pdf, "application/pdf")},
        headers=headers_b,
    )
    assert upload.status_code == 202, upload.text
    report_id = upload.json()["id"]

    # User A attempts to read B's report → must be 404/403, never the data
    resp = client.get(f"/api/v1/reports/{report_id}", headers=headers_a)
    assert resp.status_code in (403, 404)

    # Download + delete + compare are equally protected
    assert client.get(f"/api/v1/reports/{report_id}/download", headers=headers_a).status_code in (403, 404)
    assert client.delete(f"/api/v1/reports/{report_id}", headers=headers_a).status_code in (403, 404)
    assert client.get(f"/api/v1/reports/compare?a={report_id}&b={report_id}", headers=headers_a).status_code in (400, 403, 404)


def test_user_a_cannot_touch_user_b_contacts_and_doctors(client):
    headers_a = auth_headers(client, "sec-c@example.com")
    headers_b = auth_headers(client, "sec-d@example.com")

    contact = client.post(
        "/api/v1/emergency-contacts",
        json={"name": "Emergency", "relationship": "family", "phone": "+91-90000-1111"},
        headers=headers_b,
    )
    contact_id = contact.json()["id"]
    assert client.delete(
        f"/api/v1/emergency-contacts/{contact_id}", headers=headers_a
    ).status_code in (403, 404)

    doctor = client.post(
        "/api/v1/doctors",
        json={"doctor_name": "Dr. Private", "specialty": "Cardiology"},
        headers=headers_b,
    )
    doctor_id = doctor.json()["id"]
    assert client.put(
        f"/api/v1/doctors/{doctor_id}",
        json={"doctor_name": "Hacked", "is_family_doctor": True},
        headers=headers_a,
    ).status_code in (403, 404)

    # B's data unchanged
    doctors = client.get("/api/v1/doctors", headers=headers_b).json()
    assert doctors[0]["doctor_name"] == "Dr. Private"


def test_unauthenticated_access_blocked(client):
    for method, path in [
        ("get", "/api/v1/profile"),
        ("get", "/api/v1/family/members"),
        ("post", "/api/v1/health-metrics"),
        ("get", "/api/v1/timeline"),
        ("post", "/api/v1/assistant/chat"),
    ]:
        call = getattr(client, method)
        resp = call(path, **({"json": {}} if method == "post" else {}))
        assert resp.status_code == 403, f"{method} {path} should require auth"


def test_malicious_file_rejected(client):
    headers = auth_headers(client, "sec-e@example.com")
    fake = b"MZ\x90\x00this-is-actually-an-executable"
    resp = client.post(
        "/api/v1/reports",
        files={"file": ("malware.pdf", fake, "application/pdf")},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["error"]["message"] or "Unsupported" in resp.json()["error"]["message"]


def test_path_traversal_in_storage_key_blocked():
    from app.services.storage import LocalStorageService
    import pytest

    svc = LocalStorageService()
    with pytest.raises(ValueError):
        svc._path_for("../../etc/passwd")
