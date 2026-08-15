"""Dashboard statistics and analytics (government)."""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_government
from app.core.enums import PotholeStatus, Role
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Pothole, Repair, Report, User
from app.schemas.dashboard import AnalyticsData, DashboardStats, SeverityStat, StatCard, WardStat
from app.services.road_health import compute_road_health

settings = get_settings()
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/statistics", response_model=DashboardStats)
def statistics(db: Session = Depends(get_db), _: User = Depends(require_government)):
    total = db.execute(select(func.count()).select_from(Pothole)).scalar_one()
    critical = db.execute(
        select(func.count()).select_from(Pothole).where(Pothole.severity == "CRITICAL")
    ).scalar_one()
    pending = db.execute(
        select(func.count()).select_from(Pothole)
        .where(Pothole.status.in_([PotholeStatus.SUBMITTED, PotholeStatus.AI_ANALYZED,
                                   PotholeStatus.PENDING_VERIFICATION]))
    ).scalar_one()
    in_progress = db.execute(
        select(func.count()).select_from(Pothole).where(Pothole.status == PotholeStatus.IN_PROGRESS)
    ).scalar_one()
    completed = db.execute(
        select(func.count()).select_from(Pothole)
        .where(Pothole.status.in_([PotholeStatus.CLOSED, PotholeStatus.COMPLETED,
                                   PotholeStatus.CITIZEN_VERIFICATION]))
    ).scalar_one()
    budget = db.execute(select(func.coalesce(func.sum(Pothole.estimated_cost), 0.0))).scalar_one()
    actual = db.execute(select(func.coalesce(func.sum(Repair.actual_cost), 0.0))).scalar_one()

    repairs = db.execute(select(Repair.assigned_at, Repair.completion_date)).all()
    days = [(c - a).total_seconds() / 86400.0 for a, c in repairs if a and c]
    avg_days = round(sum(days) / len(days), 1) if days else 0.0

    cards = [
        StatCard(key="total", label="Total Potholes", value=total),
        StatCard(key="critical", label="Critical Potholes", value=critical),
        StatCard(key="pending", label="Pending Verification", value=pending),
        StatCard(key="in_progress", label="Repairs In Progress", value=in_progress),
        StatCard(key="completed", label="Completed Repairs", value=completed),
        StatCard(key="budget", label="Estimated Repair Budget", value=round(budget), suffix="₹"),
        StatCard(key="actual", label="Actual Repair Cost", value=round(actual), suffix="₹"),
        StatCard(key="avg_time", label="Average Repair Time", value=avg_days, suffix=" days"),
    ]
    return DashboardStats(
        total_potholes=total, critical_potholes=critical, pending_verification=pending,
        repairs_in_progress=in_progress, completed_repairs=completed,
        estimated_repair_budget=round(budget, 2), actual_repair_cost=round(actual, 2),
        average_repair_days=avg_days, cards=cards,
    )


@router.get("/severity", response_model=list[SeverityStat])
def severity_stats(db: Session = Depends(get_db), _: User = Depends(require_government)):
    rows = db.execute(
        select(Pothole.severity, func.count()).group_by(Pothole.severity)
    ).all()
    return [SeverityStat(severity=r[0], count=r[1]) for r in rows]


@router.get("/wards", response_model=list[WardStat])
def ward_stats(db: Session = Depends(get_db), _: User = Depends(require_government)):
    rows = db.execute(
        select(Pothole.ward, func.count(), func.sum(Pothole.estimated_cost))
        .group_by(Pothole.ward)
    ).all()
    return [WardStat(ward=r[0] or "-", count=r[1], estimated_cost=round(r[2] or 0, 2)) for r in rows]


@router.get("/analytics", response_model=AnalyticsData)
def analytics(db: Session = Depends(get_db), _: User = Depends(require_government)):
    rows = db.execute(
        select(Pothole.severity, func.count()).group_by(Pothole.severity)
    ).all()
    severity = [SeverityStat(severity=r[0], count=r[1]) for r in rows]

    ward_rows = db.execute(
        select(Pothole.ward, func.count(), func.sum(Pothole.estimated_cost))
        .group_by(Pothole.ward)
    ).all()
    by_ward = [WardStat(ward=r[0] or "-", count=r[1], estimated_cost=round(r[2] or 0, 2)) for r in ward_rows]

    # Reports over time (last 30 days, daily)
    start = datetime.utcnow() - timedelta(days=30)
    report_rows = db.execute(
        select(func.date(Report.created_at), func.count())
        .where(Report.created_at >= start).group_by(func.date(Report.created_at)).order_by(func.date(Report.created_at))
    ).all()
    reports_over_time = [{"date": r[0], "count": r[1]} for r in report_rows]

    repair_rows = db.execute(
        select(func.date(Repair.completion_date), func.count())
        .where(Repair.completion_date.isnot(None)).group_by(func.date(Repair.completion_date))
    ).all()
    repairs_over_time = [{"date": r[0], "count": r[1]} for r in repair_rows]

    budget = db.execute(select(func.coalesce(func.sum(Pothole.estimated_cost), 0.0))).scalar_one()
    actual = db.execute(select(func.coalesce(func.sum(Repair.actual_cost), 0.0))).scalar_one()

    repairs = db.execute(select(Repair.assigned_at, Repair.completion_date)).all()
    days = [(c - a).total_seconds() / 86400.0 for a, c in repairs if a and c]
    avg_time = round(sum(days) / len(days), 1) if days else 0.0

    roads = db.execute(select(Pothole.road).distinct()).scalars().all()
    road_health = []
    for road in roads:
        score = compute_road_health(db, road)
        if score is not None:
            road_health.append({"road": road, "health_score": score})
    road_health = sorted(road_health, key=lambda r: r["health_score"])[:10]

    closed = db.execute(
        select(func.count()).select_from(Pothole)
        .where(Pothole.status.in_([PotholeStatus.CLOSED, PotholeStatus.COMPLETED]))
    ).scalar_one()
    open_count = max(0, db.execute(select(func.count()).select_from(Pothole)).scalar_one() - closed)

    top_rows = db.execute(
        select(Pothole.road, func.count())
        .where(Pothole.road != "").group_by(Pothole.road).order_by(func.count().desc()).limit(10)
    ).all()
    top_roads = [{"road": r[0], "count": r[1]} for r in top_rows]

    return AnalyticsData(
        severity=severity,
        by_ward=by_ward,
        reports_over_time=reports_over_time,
        repairs_over_time=repairs_over_time,
        estimated_vs_actual={"estimated": round(budget, 2), "actual": round(actual, 2)},
        avg_repair_time=avg_time,
        road_health=road_health,
        pending_vs_completed={"pending": open_count, "completed": closed},
        top_damaged_roads=top_roads,
    )
