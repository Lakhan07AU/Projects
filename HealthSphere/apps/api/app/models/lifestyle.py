"""Lifestyle profiles and logs (exercise, diet, sleep)."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LifestyleProfile(Base):
    __tablename__ = "lifestyle_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    activity_level: Mapped[Optional[str]] = mapped_column(String(32))  # sedentary|light|moderate|active|athlete
    sleep_goal_hours: Mapped[Optional[float]] = mapped_column(default=8.0)
    diet_type: Mapped[Optional[str]] = mapped_column(String(32))  # vegetarian|vegan|eggetarian|non_vegetarian|other
    goal: Mapped[Optional[str]] = mapped_column(String(32))  # maintain|lose_weight|gain_muscle|improve_fitness
    smoking_status: Mapped[Optional[str]] = mapped_column(String(16))
    alcohol_frequency: Mapped[Optional[str]] = mapped_column(String(16))
    stress_level: Mapped[Optional[str]] = mapped_column(String(16))  # low|moderate|high
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    activity: Mapped[str] = mapped_column(String(128), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(nullable=False)
    intensity: Mapped[Optional[str]] = mapped_column(String(16))  # light|moderate|intense
    performed_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DietLog(Base):
    __tablename__ = "diet_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    meal: Mapped[str] = mapped_column(String(255), nullable=False)
    meal_type: Mapped[Optional[str]] = mapped_column(String(16))  # breakfast|lunch|dinner|snack
    calories: Mapped[Optional[float]] = mapped_column(nullable=True)
    logged_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SleepLog(Base):
    __tablename__ = "sleep_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    hours: Mapped[float] = mapped_column(nullable=False)
    quality: Mapped[Optional[str]] = mapped_column(String(16))  # poor|fair|good|excellent
    logged_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
