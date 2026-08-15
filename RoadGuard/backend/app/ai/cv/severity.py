"""Severity scoring engine.

Produces a 0-100 severity score and a category label.

NOTE: thresholds below are project-configurable values used for prioritisation
and reporting, NOT official engineering standards.
"""
from __future__ import annotations

from app.core.enums import Severity

# Configurable thresholds (0-100)
THRESHOLDS = {
    Severity.LOW: (0, 25),
    Severity.MEDIUM: (26, 50),
    Severity.HIGH: (51, 75),
    Severity.CRITICAL: (76, 100),
}

# Weights used in the demo pipeline (no depth/traffic data available).
WEIGHTS = {"area": 0.5, "confidence": 0.3, "reports": 0.2}


def classify(score: float) -> Severity:
    for severity, (lo, hi) in THRESHOLDS.items():
        if lo <= score <= hi:
            return severity
    return Severity.CRITICAL


def score_from_detection(
    area_pixels: float,
    image_pixels: float,
    confidence: float,
    reports: int = 1,
    traffic_level: int = 3,  # 1-5
    road_importance: int = 3,  # 1-5
) -> dict:
    """Compute a severity score. When physical data (depth/traffic) is missing
    the engine falls back to image-derived signals and clearly states it."""
    if image_pixels <= 0:
        image_pixels = 1
    area_ratio = min(1.0, area_pixels / max(1.0, image_pixels * 0.05))
    area_component = area_ratio * 100

    score = (
        area_component * WEIGHTS["area"]
        + (confidence * 100) * WEIGHTS["confidence"]
        + min(1.0, reports / 10.0) * 100 * WEIGHTS["reports"]
    )
    # Traffic + road importance as small modifiers (only when data is provided).
    score += (traffic_level - 3) * 2 + (road_importance - 3) * 2
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 1),
        "severity": classify(score).value,
        "method": "image-signal-estimate",
        "note": "Estimated severity for prioritisation. Official engineering assessment is still required.",
    }


def score_from_pothole(
    severity_score: float,
    traffic_level: int = 3,
    road_importance: int = 3,
    reports: int = 1,
) -> dict:
    score = severity_score + (traffic_level - 3) * 3 + (road_importance - 3) * 3
    score = max(0.0, min(100.0, score + min(10, reports - 1) * 1.5))
    return {"score": round(score, 1), "severity": classify(score).value}
