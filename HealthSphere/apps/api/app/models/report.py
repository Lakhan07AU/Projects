"""Medical reports, extracted entities, and document processing jobs."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReportStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    analyzing = "analyzing"
    complete = "complete"
    failed = "failed"


REPORT_CATEGORIES = [
    "cbc", "lipid_profile", "hba1c", "blood_glucose", "thyroid", "liver_function",
    "kidney_function", "ecg", "imaging", "prescription", "doctor_note", "other",
]


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(String(32), default="other", index=True)
    report_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    laboratory: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, native_enum=False, length=16), default=ReportStatus.uploaded, index=True
    )
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # never logged
    analysis_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    entities: Mapped[list["MedicalEntity"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class MedicalEntity(Base):
    """One structured value extracted from a report, with provenance + confidence."""
    __tablename__ = "medical_entities"
    __table_args__ = (
        Index("ix_entities_report_name", "report_id", "test_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("medical_reports.id", ondelete="CASCADE"), index=True, nullable=False)
    test_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    reference_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reference_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    abnormal_flag: Mapped[bool] = mapped_column(default=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # 0..1
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # provenance snippet
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped[MedicalReport] = relationship(back_populates="entities")


class DocumentProcessingJob(Base):
    __tablename__ = "document_processing_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("medical_reports.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="queued")  # queued|running|complete|failed
    stage: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # ocr|classification|extraction|analysis
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
