"""Road health score (0-100).

Inputs: pothole density, severity, unresolved potholes, report frequency.
90 = Excellent, 75 = Good, 55 = Moderate, 35 = Poor, 20 = Critical.
This is an indicative score, not an engineering rating.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import PotholeStatus, Severity
from app.db.models import Pothole, Report


def road_health(
    density_per_km: float,
    severity_score: float,
    unresolved_ratio: float,
    report_frequency: float,
) -> float:
    score = 100.0
    score -= min(40.0, density_per_km * 8.0)
    score -= severity_score * 0.4
    score -= unresolved_ratio * 30.0
    score -= min(20.0, report_frequency * 4.0)
    return max(0.0, min(100.0, round(score, 1)))


def compute_road_health(db: Session, road: str) -> float | None:
    if not road:
        return None
    potholes = db.execute(select(Pothole).where(Pothole.road == road)).scalars().all()
    if not potholes:
        return None
    total = len(potholes)
    unresolved = [p for p in potholes if p.status in (
        PotholeStatus.PENDING_VERIFICATION,
        PotholeStatus.VERIFIED,
        PotholeStatus.PRIORITIZED,
        PotholeStatus.ASSIGNED,
        PotholeStatus.IN_PROGRESS,
        PotholeStatus.SUBMITTED,
        PotholeStatus.AI_ANALYZED,
    )]
    avg_severity = sum(p.severity_score for p in potholes) / total
    report_freq = sum(p.report_count for p in potholes) / total
    density = total / max(0.5, road_length_guess(db, road))
    return road_health(density, avg_severity, len(unresolved) / total, report_freq)


def road_length_guess(db: Session, road: str) -> float:
    from app.db.models import RoadSegment

    seg = db.execute(select(RoadSegment).where(RoadSegment.name == road)).scalar_one_or_none()
    return seg.length_km if seg and seg.length_km else 2.0


def health_label(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Moderate"
    if score >= 30:
        return "Poor"
    return "Critical"
