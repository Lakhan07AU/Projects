from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import PotholeStatus, Priority, Severity


class PotholeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    pothole_code: str
    latitude: float
    longitude: float
    city: str
    district: str
    state: str
    ward: str
    road: str
    severity: Severity
    severity_score: float
    confidence: float
    estimated_area: float
    repair_area: float
    estimated_cost: float
    actual_cost: float | None
    priority: Priority
    priority_score: float
    status: PotholeStatus
    report_count: int
    road_health: float | None
    source: str
    before_image: str | None
    after_image: str | None
    created_at: datetime


class PotholeDetail(PotholeOut):
    priority_override_reason: str | None
    priority_modified_by: str | None
    priority_modified_at: datetime | None
    rejected_reason: str | None
    verified_by: str | None
    verified_at: datetime | None


class VerifyRequest(BaseModel):
    action: str  # verify | reject
    reason: str | None = None


class AssignRequest(BaseModel):
    team_id: int
    deadline: str | None = None
    deadline_days: int = 10


class UpdateStatusRequest(BaseModel):
    status: PotholeStatus
    note: str | None = None


class OverridePriorityRequest(BaseModel):
    priority: Priority
    priority_score: float | None = None
    reason: str = ""
