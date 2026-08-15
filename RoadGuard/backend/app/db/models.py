"""SQLAlchemy ORM models.

Portable across SQLite (demo) and PostgreSQL + PostGIS (production).
Spatial data is stored as latitude/longitude floats plus an optional WKT
``geometry`` string that is generated when PostGIS is available.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    NotifType,
    PotholeStatus,
    Priority,
    Role,
    Severity,
    VerificationResult,
)
from app.db.database import Base


def new_uuid() -> str:
    return uuid.uuid4().hex[:12]


def timestamp() -> datetime:
    return datetime.utcnow()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=timestamp, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=timestamp, onupdate=timestamp, nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False, length=20), default=Role.CITIZEN, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    reports: Mapped[list[Report]] = relationship(back_populates="user")


class Ward(Base, TimestampMixin):
    __tablename__ = "wards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    city: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    district: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    state: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    boundary_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)


class RoadSegment(Base, TimestampMixin):
    __tablename__ = "road_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    road_number: Mapped[str] = mapped_column(String(60), default="", nullable=False)
    road_class: Mapped[str] = mapped_column(String(20), default="MDR", nullable=False)
    ward_id: Mapped[int | None] = mapped_column(ForeignKey("wards.id"), nullable=True)
    length_km: Mapped[float] = mapped_column(Float, default=0.0)
    health_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    ward: Mapped[Ward | None] = relationship()


class Pothole(Base, TimestampMixin):
    __tablename__ = "potholes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_uuid)
    pothole_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geometry: Mapped[str | None] = mapped_column(Text, nullable=True)  # WKT POINT

    city: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    district: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    state: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    ward: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    road: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    ward_id: Mapped[int | None] = mapped_column(ForeignKey("wards.id"), nullable=True)
    road_id: Mapped[int | None] = mapped_column(ForeignKey("road_segments.id"), nullable=True)

    severity: Mapped[Severity] = mapped_column(Enum(Severity, native_enum=False, length=20), default=Severity.LOW)
    severity_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_area: Mapped[float] = mapped_column(Float, default=0.0)
    repair_area: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    priority: Mapped[Priority] = mapped_column(Enum(Priority, native_enum=False, length=20), default=Priority.MEDIUM)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)
    priority_override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_modified_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    priority_modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    status: Mapped[PotholeStatus] = mapped_column(Enum(PotholeStatus, native_enum=False, length=30), default=PotholeStatus.SUBMITTED)
    report_count: Mapped[int] = mapped_column(Integer, default=1)
    road_health: Mapped[float | None] = mapped_column(Float, nullable=True)

    source: Mapped[str] = mapped_column(String(20), default="REPORT")
    before_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    after_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    reports: Mapped[list[Report]] = relationship(back_populates="pothole", foreign_keys="Report.pothole_id")
    repair: Mapped[Repair | None] = relationship(back_populates="pothole", uselist=False)


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_uuid)
    report_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    pothole_id: Mapped[str | None] = mapped_column(
        ForeignKey("potholes.id"), nullable=True, index=True
    )

    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    city: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    district: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    state: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    ward: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    road: Mapped[str] = mapped_column(String(200), default="", nullable=False)

    detected: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[Severity] = mapped_column(Enum(Severity, native_enum=False, length=20), default=Severity.LOW)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED")

    user: Mapped[User | None] = relationship(back_populates="reports")
    pothole: Mapped[Pothole | None] = relationship(back_populates="reports", foreign_keys=[pothole_id])


class Detection(Base, TimestampMixin):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[str | None] = mapped_column(ForeignKey("reports.id"), nullable=True)
    pothole_id: Mapped[str | None] = mapped_column(ForeignKey("potholes.id"), nullable=True)
    class_name: Mapped[str] = mapped_column(String(60), default="pothole")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    bbox: Mapped[dict] = mapped_column(JSON, default=dict)
    area_pixels: Mapped[float] = mapped_column(Float, default=0.0)


class AIAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id"), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), default="demo")
    model_version: Mapped[str] = mapped_column(String(60), default="demo-v1")
    demo_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    detected: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(20), default="LOW")
    severity_score: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_area: Mapped[float] = mapped_column(Float, default=0.0)
    repair_area: Mapped[float] = mapped_column(Float, default=0.0)
    raw: Mapped[dict] = mapped_column(JSON, default=dict)


class RepairTeam(Base, TimestampMixin):
    __tablename__ = "repair_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    contact: Mapped[str] = mapped_column(String(60), default="")
    manager_name: Mapped[str] = mapped_column(String(120), default="")
    city: Mapped[str] = mapped_column(String(120), default="")
    ward: Mapped[str] = mapped_column(String(120), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Repair(Base, TimestampMixin):
    __tablename__ = "repairs"
    __table_args__ = (UniqueConstraint("pothole_id", name="uq_repairs_pothole"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_uuid)
    pothole_id: Mapped[str] = mapped_column(ForeignKey("potholes.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("repair_teams.id"), nullable=True)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    repair_area: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(30), default="SCHEDULED")
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completion_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verification_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    after_image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    pothole: Mapped[Pothole] = relationship(back_populates="repair")
    team: Mapped[RepairTeam | None] = relationship()
    updates: Mapped[list[RepairUpdate]] = relationship(back_populates="repair")


class RepairUpdate(Base, TimestampMixin):
    __tablename__ = "repair_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repair_id: Mapped[str] = mapped_column(ForeignKey("repairs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(120), nullable=True)

    repair: Mapped[Repair] = relationship(back_populates="updates")


class CostRate(Base, TimestampMixin):
    __tablename__ = "cost_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rate_key: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    unit: Mapped[str] = mapped_column(String(40), default="INR/sqm")
    value: Mapped[float] = mapped_column(Float, default=0.0)
    effective_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    previous_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(120), nullable=True)


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    pothole_id: Mapped[str | None] = mapped_column(ForeignKey("potholes.id"), nullable=True)
    type: Mapped[NotifType] = mapped_column(Enum(NotifType, native_enum=False, length=20), default=NotifType.SYSTEM)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str] = mapped_column(String(300), default="")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class ModelVersion(Base, TimestampMixin):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(60), nullable=False)
    path: Mapped[str] = mapped_column(String(500), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user_name: Mapped[str] = mapped_column(String(120), default="")
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    object_type: Mapped[str] = mapped_column(String(60), default="")
    object_id: Mapped[str] = mapped_column(String(60), default="")
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip: Mapped[str] = mapped_column(String(60), default="")
