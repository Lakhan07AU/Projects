"""Duplicate complaint detection.

A new report is attached to an existing open pothole when:
1. It is close enough geographically (GPS distance), AND
2. The existing pothole is not closed/rejected, AND
3. Optionally: image similarity / report age limits.

The matching pothole's ``report_count`` is incremented instead of creating a
new pothole.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.cv.area_estimator import haversine_km
from app.core.enums import PotholeStatus
from app.db.models import Pothole

DUP_DISTANCE_M = 50.0  # 50 m radius
DUP_MAX_AGE_DAYS = 60


def find_duplicate(
    db: Session,
    latitude: float,
    longitude: float,
    image_signature: str | None = None,
) -> Pothole | None:
    """Return an existing active pothole that this report should attach to."""
    if latitude is None or longitude is None:
        return None

    open_statuses = [
        s for s in PotholeStatus if s not in (PotholeStatus.CLOSED, PotholeStatus.REJECTED)
    ]
    candidates = db.execute(
        select(Pothole).where(Pothole.status.in_(open_statuses))
    ).scalars().all()

    best: Pothole | None = None
    best_km = DUP_DISTANCE_M / 1000.0
    for p in candidates:
        dist = haversine_km(latitude, longitude, p.latitude, p.longitude)
        if dist <= best_km:
            best_km = dist
            best = p
    return best
