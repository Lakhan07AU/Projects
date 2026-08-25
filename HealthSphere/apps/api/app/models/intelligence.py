"""Health intelligence: recommendations, clinical rules & sources, timeline."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RecommendationKind(str, enum.Enum):
    preventive_care = "preventive_care"
    specialty_discussion = "specialty_discussion"
    lifestyle = "lifestyle"
    trend_followup = "trend_followup"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ClinicalSource(Base):
    __tablename__ = "clinical_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # e.g. "who-physical-activity"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    publication_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    last_reviewed: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)


class ClinicalRule(Base):
    """Deterministic rule. The LLM may explain a fired rule but never invents one."""
    __tablename__ = "clinical_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    condition: Mapped[str] = mapped_column(String(128), index=True, nullable=False)  # risk area / trigger domain
    population: Mapped[str] = mapped_column(String(128), default="adults")  # adults|adults_40_plus|all etc.
    trigger: Mapped[dict] = mapped_column(JSON, nullable=False)  # declarative predicate
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_key: Mapped[Optional[str]] = mapped_column(ForeignKey("clinical_sources.key"), nullable=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority, native_enum=False, length=8), default=Priority.low)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[str] = mapped_column(String(16), default="1.0")
    last_reviewed: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        Index("ix_reco_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    kind: Mapped[RecommendationKind] = mapped_column(
        Enum(RecommendationKind, native_enum=False, length=32), nullable=False
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    guidance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority, native_enum=False, length=8), default=Priority.low)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # engine confidence 0..1
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class TimelineEventType(str, enum.Enum):
    report_uploaded = "report_uploaded"
    report_analyzed = "report_analyzed"
    lab_result = "lab_result"
    measurement = "measurement"
    doctor_visit = "doctor_visit"
    condition_added = "condition_added"
    medication_added = "medication_added"
    family_history = "family_history"
    lifestyle = "lifestyle"
    recommendation = "recommendation"
    reminder = "reminder"


class HealthTimelineEvent(Base):
    __tablename__ = "health_timeline_events"
    __table_args__ = (
        Index("ix_timeline_user_date", "user_id", "event_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[TimelineEventType] = mapped_column(
        Enum(TimelineEventType, native_enum=False, length=32), nullable=False
    )
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="system")
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    related_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
