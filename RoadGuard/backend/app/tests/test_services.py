"""Service-level tests: severity, area, cost, priority, road health, duplicates."""
from __future__ import annotations

import pytest

from app.ai.cv.area_estimator import AreaEstimator, haversine_km
from app.ai.cv.severity import classify, score_from_detection
from app.services.cost_estimator import calculate_repair_area, estimate_cost
from app.services.priority import compute_priority, priority_label
from app.services.road_health import road_health


# ---------- Severity ----------

def test_severity_classification_thresholds():
    assert classify(10) == "LOW"
    assert classify(40) == "MEDIUM"
    assert classify(60) == "HIGH"
    assert classify(90) == "CRITICAL"


def test_severity_score_bounds():
    result = score_from_detection(0, 100000, 1.0, reports=50)
    assert 0 <= result["score"] <= 100
    assert result["severity"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert "estimate" in result["method"]


# ---------- Area ----------

def test_area_estimate_scales_with_pixels():
    est = AreaEstimator(pixels_per_metre=30)
    a = est.estimate(900, 0.9)
    b = est.estimate(1800, 0.9)
    assert a["estimated_area_m2"] == 1.0
    assert b["estimated_area_m2"] == 2.0
    assert a["label"] == "Estimated Area"


def test_area_estimate_zero():
    est = AreaEstimator()
    result = est.estimate(0, 0.9)
    assert result["estimated_area_m2"] == 0.0


def test_haversine_known_distance():
    # ~111 km per degree of latitude
    assert 110 < haversine_km(0, 0, 1, 0) < 112


# ---------- Cost ----------

def test_repair_area_margin():
    # Default margin 20%: 3.5 -> 4.2
    assert calculate_repair_area(3.5) == pytest.approx(4.2)


def test_cost_breakdown_sums_to_total():
    cost = estimate_cost(4.2)
    total = cost["material"] + cost["labor"] + cost["equipment"] + cost["transport"] + cost["contingency"]
    assert cost["total"] == pytest.approx(total)
    assert cost["label"] == "AI-assisted preliminary estimate"
    assert cost["material"] == pytest.approx(4.2 * 2200)


# ---------- Priority ----------

def test_priority_score_and_label():
    result = compute_priority(severity_score=95, traffic_level=5, road_importance=5,
                              supporting_reports=20, pending_days=30)
    assert result["priority"] == "CRITICAL"
    assert 0 <= result["score"] <= 100


def test_priority_label_buckets():
    assert priority_label(90) == "CRITICAL"
    assert priority_label(70) == "HIGH"
    assert priority_label(50) == "MEDIUM"
    assert priority_label(20) == "LOW"


# ---------- Road health ----------

def test_road_health_score():
    score = road_health(density_per_km=1.0, severity_score=20, unresolved_ratio=0.1,
                        report_frequency=1.0)
    assert 0 <= score <= 100
    worse = road_health(density_per_km=5.0, severity_score=80, unresolved_ratio=0.9,
                        report_frequency=5.0)
    assert worse < score
