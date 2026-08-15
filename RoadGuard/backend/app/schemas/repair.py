from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RepairOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    pothole_id: str
    team_id: int | None
    estimated_cost: float
    actual_cost: float | None
    repair_area: float
    status: str
    assigned_at: datetime | None
    accepted_at: datetime | None
    start_date: datetime | None
    completion_date: datetime | None
    deadline: datetime | None
    verification_score: float | None
    after_image: str | None


class RepairWithPothole(RepairOut):
    pothole: dict[str, Any] | None = None


class CompleteRepairRequest(BaseModel):
    actual_cost: float
    note: str = ""


class RepairUpdateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    note: str
    image_path: str | None
    cost: float | None
    created_by: str | None
    created_at: datetime
