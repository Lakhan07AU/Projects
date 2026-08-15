"""Government assistant.

The assistant NEVER runs arbitrary SQL. It calls a fixed set of controlled
functions that return aggregated statistics from the database. The LLM (when
available) only converts those structured results into natural language.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.genai.llm_service import llm_service
from app.ai.genai.prompt_manager import ASSISTANT_SYSTEM_PROMPT
from app.core.enums import PotholeStatus
from app.db.models import Pothole, Repair, Ward


def get_pothole_statistics(db: Session) -> dict:
    total = db.execute(select(func.count()).select_from(Pothole)).scalar_one()
    critical = db.execute(
        select(func.count()).select_from(Pothole).where(Pothole.severity == "CRITICAL")
    ).scalar_one()
    pending = db.execute(
        select(func.count()).select_from(Pothole)
        .where(Pothole.status.in_([PotholeStatus.SUBMITTED, PotholeStatus.AI_ANALYZED,
                                   PotholeStatus.PENDING_VERIFICATION]))
    ).scalar_one()
    repaired = db.execute(
        select(func.count()).select_from(Pothole)
        .where(Pothole.status.in_([PotholeStatus.CLOSED, PotholeStatus.COMPLETED]))
    ).scalar_one()
    return {
        "total_potholes": total,
        "critical_potholes": critical,
        "pending_verification": pending,
        "repaired": repaired,
    }


def get_ward_statistics(db: Session) -> list[dict]:
    rows = db.execute(
        select(Pothole.ward, func.count(), func.sum(Pothole.estimated_cost))
        .group_by(Pothole.ward).order_by(func.count().desc())
    ).all()
    return [{"ward": r[0] or "-", "count": r[1], "estimated_cost": round(r[2] or 0, 2)} for r in rows]


def get_repair_budget(db: Session, ward: str | None = None) -> float:
    stmt = select(func.coalesce(func.sum(Pothole.estimated_cost), 0.0))
    if ward:
        stmt = stmt.where(Pothole.ward == ward)
    return round(db.execute(stmt).scalar_one(), 2)


def get_priority_potholes(db: Session, limit: int = 10) -> list[dict]:
    rows = db.execute(
        select(Pothole).order_by(Pothole.priority_score.desc()).limit(limit)
    ).scalars().all()
    return [
        {
            "pothole_code": p.pothole_code,
            "ward": p.ward,
            "road": p.road,
            "severity": p.severity.value,
            "priority": p.priority.value,
            "priority_score": p.priority_score,
            "status": p.status.value,
            "estimated_cost": p.estimated_cost,
        }
        for p in rows
    ]


def get_repair_time_statistics(db: Session) -> dict:
    rows = db.execute(select(Repair.completion_date, Repair.assigned_at)).all()
    days = []
    for completion, assigned in rows:
        if completion and assigned:
            days.append((completion - assigned).total_seconds() / 86400.0)
    return {
        "completed_repairs": len(days),
        "average_repair_days": round(sum(days) / len(days), 1) if days else None,
    }


def get_road_health(db: Session) -> list[dict]:
    from app.services.road_health import compute_road_health

    roads = db.execute(select(Pothole.road).distinct()).scalars().all()
    result = []
    for road in roads:
        score = compute_road_health(db, road)
        if score is not None:
            result.append({"road": road, "health_score": score})
    return sorted(result, key=lambda r: r["health_score"])[:20]


TOOLS: dict[str, dict] = {
    "get_pothole_statistics": {"func": get_pothole_statistics, "params": ()},
    "get_ward_statistics": {"func": get_ward_statistics, "params": ()},
    "get_repair_budget": {"func": get_repair_budget, "params": ("ward",)},
    "get_priority_potholes": {"func": get_priority_potholes, "params": ()},
    "get_repair_time_statistics": {"func": get_repair_time_statistics, "params": ()},
    "get_road_health": {"func": get_road_health, "params": ()},
}


def _template_answer(question: str, results: dict) -> str:
    lines = [f"**Question:** {question}", ""]
    for key, value in results.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"- {key}: no data")
                continue
            lines.append(f"- {key}:")
            for item in value[:10]:
                if isinstance(item, dict):
                    lines.append("  - " + ", ".join(f"{k}: {v}" for k, v in item.items()))
                else:
                    lines.append(f"  - {item}")
        else:
            lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("*(Template answer - LLM unavailable)*")
    return "\n".join(lines)


def answer_question(db: Session, question: str) -> dict:
    """Route the question to the relevant controlled function."""
    q = question.lower()
    results: dict[str, object] = {}

    if "budget" in q or "cost" in q:
        ward = None
        results["repair_budget_total_inr"] = get_repair_budget(db)
        if "ward" in q:
            for row in get_ward_statistics(db):
                if row["ward"].lower() in q:
                    ward = row["ward"]
                    break
            if ward:
                results["ward"] = ward
                results["ward_budget_inr"] = get_repair_budget(db, ward)
    if "ward" in q:
        results["wards_by_pothole_count"] = get_ward_statistics(db)
    if "priority" in q or "top" in q:
        results["top_priority_potholes"] = get_priority_potholes(db)
    if "repair time" in q or "average repair" in q or "how long" in q:
        results["repair_time"] = get_repair_time_statistics(db)
    if "road" in q or "deteriorat" in q or "health" in q:
        results["road_health"] = get_road_health(db)
    if "critical" in q or "pending" in q or "statistics" in q or "pothole" in q and not results:
        results["statistics"] = get_pothole_statistics(db)

    if not results:
        results["statistics"] = get_pothole_statistics(db)

    result = llm_service.complete(
        ASSISTANT_SYSTEM_PROMPT,
        f"Question: {question}\nControlled backend results (JSON): {json.dumps(results, default=str)}",
        max_tokens=500,
    )
    if result["used_llm"]:
        return {"answer": result["text"], "used_llm": True, "data": results}
    return {"answer": _template_answer(question, results), "used_llm": False, "data": results}
