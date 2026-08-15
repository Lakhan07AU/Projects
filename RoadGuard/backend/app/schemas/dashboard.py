from typing import Any

from pydantic import BaseModel


class StatCard(BaseModel):
    key: str
    label: str
    value: Any
    suffix: str = ""


class DashboardStats(BaseModel):
    total_potholes: int
    critical_potholes: int
    pending_verification: int
    repairs_in_progress: int
    completed_repairs: int
    estimated_repair_budget: float
    actual_repair_cost: float
    average_repair_days: float
    cards: list[StatCard]


class SeverityStat(BaseModel):
    severity: str
    count: int


class WardStat(BaseModel):
    ward: str
    count: int
    critical: int = 0
    estimated_cost: float = 0.0


class AnalyticsData(BaseModel):
    severity: list[SeverityStat]
    by_ward: list[WardStat]
    reports_over_time: list[dict]
    repairs_over_time: list[dict]
    estimated_vs_actual: dict[str, float]
    avg_repair_time: float
    road_health: list[dict]
    pending_vs_completed: dict[str, int]
    top_damaged_roads: list[dict]
