"""Health metrics definitions and recorded values."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HealthMetric(Base):
    """Metric catalog: standard metrics are seeded; users can add custom ones."""
    __tablename__ = "health_metrics"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_metric"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )  # NULL = global/system metric
    key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # weight, blood_pressure...
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class HealthMetricValue(Base):
    __tablename__ = "health_metric_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    metric_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # e.g. diastolic BP
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="manual")  # manual | report | device
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
