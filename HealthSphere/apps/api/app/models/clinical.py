"""Normalized medical conditions and medications."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Condition(Base):
    """Normalized condition catalog (seeded + extensible)."""
    __tablename__ = "conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user_conditions: Mapped[list["UserCondition"]] = relationship(back_populates="condition")


class UserCondition(Base):
    """A condition recorded on the user's own profile (structured + free-text notes allowed)."""
    __tablename__ = "user_conditions"
    __table_args__ = (UniqueConstraint("user_id", "condition_id", name="uq_user_condition"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    condition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("conditions.id", ondelete="SET NULL"), nullable=True)
    condition_name: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnosed_year: Mapped[Optional[int]] = mapped_column(nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(32), default="active")  # active | resolved | monitoring
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    condition: Mapped[Optional[Condition]] = relationship(back_populates="user_conditions")


class Medication(Base):
    """Current/past medications recorded by the user. Never interpreted as prescriptions."""
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="active")  # active | stopped
    started_on: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
