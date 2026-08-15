"""Public map endpoints (GeoJSON)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Pothole

router = APIRouter(prefix="/api/map", tags=["map"])
public_router = APIRouter(prefix="/api", tags=["public"])


@public_router.get("/public/stats")
def public_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func, select

    from app.core.enums import PotholeStatus

    total = db.execute(select(func.count()).select_from(Pothole)).scalar_one()
    critical = db.execute(
        select(func.count()).select_from(Pothole).where(Pothole.severity == "CRITICAL")
    ).scalar_one()
    repaired = db.execute(
        select(func.count()).select_from(Pothole)
        .where(Pothole.status.in_([PotholeStatus.CLOSED, PotholeStatus.COMPLETED]))
    ).scalar_one()
    rate = round((repaired / total * 100), 1) if total else 0.0
    return {
        "total_potholes": total,
        "critical_potholes": critical,
        "repaired": repaired,
        "repair_completion_rate": rate,
    }


@public_router.get("/public/recent")
def public_recent(db: Session = Depends(get_db), limit: int = 6):
    potholes = db.query(Pothole).order_by(Pothole.created_at.desc()).limit(limit).all()
    return [
        {
            "code": p.pothole_code,
            "road": p.road,
            "ward": p.ward,
            "severity": p.severity.value,
            "status": p.status.value,
            "estimated_cost": p.estimated_cost,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in potholes
    ]


@router.get("/potholes")
def map_potholes(
    db: Session = Depends(get_db),
    severity: str | None = None,
    status: str | None = None,
    ward: str | None = None,
    limit: int = 2000,
):
    query = db.query(Pothole)
    if severity:
        query = query.filter(Pothole.severity == severity.upper())
    if status:
        query = query.filter(Pothole.status == status.upper())
    if ward:
        query = query.filter(Pothole.ward == ward)
    potholes = query.limit(limit).all()

    features = []
    for p in potholes:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [p.longitude, p.latitude]},
            "properties": {
                "id": p.id,
                "code": p.pothole_code,
                "severity": p.severity.value,
                "priority": p.priority.value,
                "status": p.status.value,
                "ward": p.ward,
                "road": p.road,
                "city": p.city,
                "estimated_area": p.estimated_area,
                "estimated_cost": p.estimated_cost,
                "report_count": p.report_count,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "road_health": p.road_health,
            },
        })
    return {"type": "FeatureCollection", "features": features}


@router.get("/nearby")
def nearby(lat: float, lon: float, radius_km: float = 2.0, db: Session = Depends(get_db)):
    from app.ai.cv.area_estimator import haversine_km

    potholes = db.query(Pothole).all()
    result = [
        {
            "id": p.id,
            "code": p.pothole_code,
            "severity": p.severity.value,
            "status": p.status.value,
            "road": p.road,
            "ward": p.ward,
            "distance_km": round(haversine_km(lat, lon, p.latitude, p.longitude), 3),
            "latitude": p.latitude,
            "longitude": p.longitude,
        }
        for p in potholes
        if haversine_km(lat, lon, p.latitude, p.longitude) <= radius_km
    ]
    return sorted(result, key=lambda r: r["distance_km"])
