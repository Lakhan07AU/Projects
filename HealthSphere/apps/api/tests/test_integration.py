"""End-to-end core integration: upload → extraction → trends → recommendations."""
from tests.conftest import SAMPLE_LAB_TEXT, auth_headers, make_pdf, wait_for_report


def test_full_health_workflow(client):
    """The master-prompt integration flow, compressed:
    profile → family → metrics → report upload → extraction → trend → recommendation → timeline → reminder."""
    headers = auth_headers(client, "e2e@example.com")

    # 1. Profile
    prof = client.put(
        "/api/v1/profile",
        json={"date_of_birth": "1980-05-10", "sex": "male", "height_cm": 175, "weight_kg": 82,
              "blood_group": "B+", "allergies": "None reported"},
        headers=headers,
    )
    assert prof.status_code == 200, prof.text
    assert prof.json()["age"] is not None

    # 2. Family member with condition (triggers diabetes screening rule later)
    member = client.post(
        "/api/v1/family/members",
        json={"relationship": "father", "name": "Father (fictional)", "living_status": "living"},
        headers=headers,
    )
    assert member.status_code == 201
    cond = client.post(
        f"/api/v1/family/members/{member.json()['id']}/conditions",
        json={"condition_name": "Type 2 Diabetes", "diagnosis_age": 55},
        headers=headers,
    )
    assert cond.status_code == 201

    # 3. Manual health metric + BP reading that fires the BP rule
    metric = client.post(
        "/api/v1/health-metrics",
        json={"metric_key": "blood_pressure", "value": 148, "secondary_value": 95, "unit": "mmHg"},
        headers=headers,
    )
    assert metric.status_code == 201

    # 4. Upload lab report (PDF with real text) → async pipeline
    pdf = make_pdf(SAMPLE_LAB_TEXT)
    upload = client.post(
        "/api/v1/reports?category=blood_panel",
        files={"file": ("lab_report.pdf", pdf, "application/pdf")},
        headers=headers,
    )
    assert upload.status_code == 202, upload.text
    report_id = upload.json()["id"]

    result = wait_for_report(client, headers, report_id)
    body = result.json()
    assert body["report"]["status"] == "complete", body["report"].get("error_message")

    # 5. Extraction produced structured values with provenance + confidence
    entities = body["entities"]
    assert len(entities) >= 3
    hba1c = next(e for e in entities if e["test_name"] == "HbA1c")
    assert hba1c["value"] == pytest_hba1c_value(hba1c["value"])
    assert hba1c["reference_low"] == 4.0 and hba1c["reference_high"] == 5.6
    assert hba1c["abnormal_flag"] is True
    assert hba1c["confidence"] > 0.5
    assert hba1c["source_text"]  # provenance present

    # 6. Lab values synced into unified metric store for trends
    trend = client.get("/api/v1/health-metrics/hba1c/trend", headers=headers)
    assert trend.status_code == 200
    assert len(trend.json()["points"]) >= 1

    # 7. Preventive-care engine generates recommendations from context
    refresh = client.post("/api/v1/recommendations/refresh", headers=headers)
    assert refresh.status_code == 202
    recos = client.get("/api/v1/recommendations", headers=headers).json()
    topics = {r["topic"] for r in recos}
    assert "cardiovascular_health" in topics          # BP 148 fired
    assert "blood_sugar_context" in topics            # age + family history fired

    # Every recommendation carries cautious guidance + source metadata
    for r in recos:
        text = (r["guidance"] or "").lower()
        assert "diagnos" not in text or "diagnosis" not in text.replace("not a diagnosis", "")
        assert any(phrase in text for phrase in ["discuss", "consider"])

    # 8. Timeline recorded the events
    timeline = client.get("/api/v1/timeline", headers=headers).json()
    event_types = {e["event_type"] for e in timeline}
    assert "measurement" in event_types and "report_analyzed" in event_types
    assert "recommendation" in event_types and "family_history" in event_types

    # 9. Specialty discussion suggestions are cautious
    specialists = client.get("/api/v1/insights/specialists", headers=headers).json()
    areas = {s["risk_area"] for s in specialists["suggestions"]}
    assert "cardiovascular_health" in areas
    for s in specialists["suggestions"]:
        assert "worth discussing" in s["reason"]

    # 10. Report comparison against itself is empty; user can correct a value
    correction = client.patch(
        f"/api/v1/reports/{report_id}/entities/{hba1c['id']}",
        json={"value": 5.2},
        headers=headers,
    )
    assert correction.status_code == 200
    corrected = correction.json()
    assert corrected["value"] == 5.2
    assert corrected["abnormal_flag"] is False   # now within range
    assert corrected["confidence"] == 1.0        # human-verified

    # 11. Reminder CRUD works
    reminder = client.post(
        "/api/v1/reminders",
        json={"type": "screening", "title": "Ask doctor about HbA1c", "due_at": "2026-09-15T09:00:00",
              "recurrence": "none"},
        headers=headers,
    )
    assert reminder.status_code == 201
    done = client.put(
        f"/api/v1/reminders/{reminder.json()['id']}", json={"status": "done"}, headers=headers
    )
    assert done.json()["status"] == "done"


def test_ai_assistant_answers_from_records(client):
    headers = auth_headers(client, "assistant@example.com")
    client.put(
        "/api/v1/profile",
        json={"date_of_birth": "1990-01-01", "height_cm": 170, "weight_kg": 68},
        headers=headers,
    )
    client.post(
        "/api/v1/health-metrics",
        json={"metric_key": "weight", "value": 70, "unit": "kg"}, headers=headers,
    )

    chat = client.post(
        "/api/v1/assistant/chat", json={"message": "Show my weight trend"}, headers=headers
    )
    assert chat.status_code == 200
    reply = chat.json()["reply"]
    assert "weight" in reply.lower()

    # Unsafe intent gets the safety response
    unsafe = client.post(
        "/api/v1/assistant/chat",
        json={"message": "Should I stop taking my medication and what medicine should I take?"},
        headers=headers,
    )
    reply = unsafe.json()["reply"]
    assert "cannot diagnose" in reply.lower() or "can't diagnose" in reply.lower()


def test_extraction_failure_is_honest(client):
    """An unreadable document must fail safely — never fabricate values."""
    headers = auth_headers(client, "ocrfail@example.com")
    # Valid PNG magic but no OCR engine available → needs_ocr path
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
    upload = client.post(
        "/api/v1/reports",
        files={"file": ("scan.png", png_bytes, "image/png")},
        headers=headers,
    )
    assert upload.status_code == 202
    result = wait_for_report(client, headers, upload.json()["id"])
    body = result.json()
    assert body["report"]["status"] == "failed"
    assert "couldn't reliably extract" in body["report"]["error_message"]
    assert "enter the relevant values manually" in body["report"]["error_message"]


def pytest_hba1c_value(v):
    class _Eq:
        def __eq__(self, other):
            return abs(other - 6.8) < 1e-6

    return _Eq()
