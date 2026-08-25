"""Doctors, emergency contacts, hospitals cache, reminders, notifications."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = (UniqueConstraint("user_id", "doctor_name", "clinic", name="uq_user_doctor"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    doctor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    clinic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_family_doctor: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )


class SymptomSeverity(str, enum.Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"


class Specialty(Base):
    """Reusable specialty reference table (seeded, never hard-coded in UI)."""
    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Symptom(Base):
    """Structured symptom catalog users select from (searchable)."""
    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class SymptomSpecialtyMap(Base):
    """Validated symptom -> specialty navigation mapping (configurable data)."""
    __tablename__ = "symptom_specialty_map"
    __table_args__ = (UniqueConstraint("symptom_id", "specialty_id", name="uq_symptom_specialty"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symptom_id: Mapped[int] = mapped_column(ForeignKey("symptoms.id", ondelete="CASCADE"), index=True, nullable=False)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id", ondelete="CASCADE"), index=True, nullable=False)
    relevance: Mapped[str] = mapped_column(String(16), default="medium")  # high|medium|low
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    source_version: Mapped[str] = mapped_column(String(32), nullable=False)
    last_reviewed: Mapped[str] = mapped_column(String(16), nullable=False)


class ConditionSpecialtyMap(Base):
    """Documented-condition keyword -> specialty mapping (configurable data)."""
    __tablename__ = "condition_specialty_map"
    __table_args__ = (UniqueConstraint("condition_keyword", "specialty_id", name="uq_condition_specialty"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    condition_keyword: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id", ondelete="CASCADE"), index=True, nullable=False)
    relevance: Mapped[str] = mapped_column(String(16), default="medium")
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    source_version: Mapped[str] = mapped_column(String(32), nullable=False)
    last_reviewed: Mapped[str] = mapped_column(String(16), nullable=False)


class UserSymptom(Base):
    """A symptom a user reports, with duration/severity context."""
    __tablename__ = "user_symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    symptom_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("symptoms.id", ondelete="SET NULL"), nullable=True
    )
    symptom_name: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_text: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    severity: Mapped[SymptomSeverity] = mapped_column(
        Enum(SymptomSeverity, native_enum=False, length=16), default=SymptomSeverity.moderate
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SpecialistRecommendation(Base):
    """Persisted output of the specialist engine. Navigation support only —
    never stored or presented as a diagnosis."""
    __tablename__ = "specialist_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    specialty_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("specialties.id", ondelete="SET NULL"), nullable=True
    )
    specialty_name: Mapped[str] = mapped_column(String(128), nullable=False)
    relevance: Mapped[str] = mapped_column(String(16), default="medium")  # high|medium|low
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    source_rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    input_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON summary of inputs used
    status: Mapped[str] = mapped_column(String(16), default="open", index=True)  # open|discussed|dismissed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship: Mapped[str] = mapped_column(String(32), default="family")
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[int] = mapped_column(default=1)  # lower = called first
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Hospital(Base):
    """Cached discovery results; populated by the HealthcareLocationProvider."""
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(32), default="mock")
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), default="hospital")  # hospital|clinic|lab|pharmacy
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    opening_hours: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    services: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ReminderRecurrence(str, enum.Enum):
    none_ = "none"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(32), default="general")  # screening|medication_followup|metric_check|general
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    recurrence: Mapped[ReminderRecurrence] = mapped_column(
        Enum(ReminderRecurrence, native_enum=False, length=16), default=ReminderRecurrence.none_
    )
    status: Mapped[str] = mapped_column(String(16), default="open", index=True)  # open|done|snoozed|cancelled
    source: Mapped[str] = mapped_column(String(64), default="user")  # user | system:<engine>
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EmergencyAlert(Base):
    """SOS trigger record. Works fully offline — no AI dependency."""

    __tablename__ = "emergency_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="sent", index=True)  # pending|sent|cancelled
    notified_names: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(16), default="in_app")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
