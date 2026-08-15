"""Priority engine.

Priority Score (0-100) from severity, traffic level, road importance,
supporting reports and pending duration. Government officials may manually
override priority; the override is audited.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.core.enums import Priority


def priority_label(score: float) -> Priority:
    if score >= 80:
        return Priority.CRITICAL
    if score >= 60:
        return Priority.HIGH
    if score >= 40:
        return Priority.MEDIUM
    return Priority.LOW


def compute_priority(
    severity_score: float,
    traffic_level: int = 3,
    road_importance: int = 3,
    supporting_reports: int = 1,
    pending_days: float = 0.0,
) -> dict:
    """Priority score. All inputs default to neutral values when unknown."""
    score = severity_score * 0.55
    score += (traffic_level / 5.0) * 100 * 0.15
    score += (road_importance / 5.0) * 100 * 0.15
    score += min(1.0, supporting_reports / 10.0) * 100 * 0.10
    score += min(1.0, pending_days / 30.0) * 100 * 0.05
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 1),
        "priority": priority_label(score).value,
        "note": "Priority for triage. Officials may override with justification.",
    }


def pending_days_since(created_at: datetime) -> float:
    now = datetime.now(timezone.utc)
    created = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
    return max(0.0, (now - created).total_seconds() / 86400.0)
