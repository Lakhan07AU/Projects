"""Cost estimation engine.

Uses deterministic formulas driven by rates from the database (CostRate table).
GenAI is NOT used to calculate costs. The result is explicitly labelled as an
"AI-assisted preliminary estimate".
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CostRate

DEFAULT_RATES: dict[str, float] = {
    "ASPHALT_PER_SQM": 2200.0,  # INR per m2
    "CONCRETE_PER_SQM": 1800.0,
    "LABOR_PER_SQM": 600.0,
    "EQUIPMENT_PER_SQM": 400.0,
    "TRANSPORT_PER_JOB": 2000.0,
    "CONTINGENCY_PERCENT": 5.0,
    "REPAIR_MARGIN_PERCENT": 20.0,
}


def load_rates(db: Session) -> dict[str, float]:
    rates = DEFAULT_RATES.copy()
    rows = db.execute(select(CostRate)).scalars().all()
    for row in rows:
        rates[row.rate_key] = row.value
    return rates


def calculate_repair_area(estimated_area: float, db: Session | None = None) -> float:
    """Recommended repair area = detected area + configurable repair margin."""
    margin_pct = DEFAULT_RATES["REPAIR_MARGIN_PERCENT"]
    if db is not None:
        row = db.execute(
            select(CostRate).where(CostRate.rate_key == "REPAIR_MARGIN_PERCENT")
        ).scalar_one_or_none()
        if row:
            margin_pct = row.value
    return round(estimated_area * (1 + margin_pct / 100.0), 2)


def estimate_cost(repair_area: float, db: Session | None = None) -> dict:
    """Preliminary cost estimate with full breakdown."""
    rates = load_rates(db) if db is not None else DEFAULT_RATES

    material = repair_area * rates["ASPHALT_PER_SQM"]
    labor = repair_area * rates["LABOR_PER_SQM"]
    equipment = repair_area * rates["EQUIPMENT_PER_SQM"]
    transport = rates["TRANSPORT_PER_JOB"]
    subtotal = material + labor + equipment + transport
    contingency = subtotal * rates["CONTINGENCY_PERCENT"] / 100.0
    total = subtotal + contingency

    return {
        "repair_area_m2": round(repair_area, 2),
        "material": round(material, 2),
        "labor": round(labor, 2),
        "equipment": round(equipment, 2),
        "transport": round(transport, 2),
        "contingency": round(contingency, 2),
        "total": round(total, 2),
        "label": "AI-assisted preliminary estimate",
        "note": "Preliminary estimate from configurable rates. Not a quotation or official cost.",
    }


def default_rates() -> dict[str, float]:
    return DEFAULT_RATES.copy()
