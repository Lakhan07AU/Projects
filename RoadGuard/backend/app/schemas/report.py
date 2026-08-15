from datetime import datetime

from pydantic import BaseModel

from app.core.enums import Severity


class DetectionOut(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]
    area_pixels: float


class AnalyzeResponse(BaseModel):
    demo_mode: bool
    detected: bool
    confidence: float
    detections: list[DetectionOut]
    severity: Severity
    severity_score: float
    estimated_area: float
    repair_area: float
    estimated_cost: float
    repair_cost_breakdown: dict
    mask_available: bool
    pixel_area: float
    message: str | None = None


class ReportCreate(BaseModel):
    analysis_id: int | None = None
    report_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    city: str = ""
    district: str = ""
    state: str = ""
    ward: str = ""
    road: str = ""
    note: str = ""


class ReportOut(BaseModel):
    id: str
    report_code: str
    pothole_id: str | None
    image_path: str | None
    latitude: float | None
    longitude: float | None
    detected: bool
    ai_confidence: float
    severity: Severity
    is_duplicate: bool
    duplicate_of: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportSubmitResponse(BaseModel):
    report: ReportOut
    duplicate: bool
    pothole: dict | None = None
