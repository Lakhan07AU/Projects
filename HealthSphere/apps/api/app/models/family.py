"""Family health history models."""
import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as orm_relationship

from app.core.database import Base


class LivingStatus(str, enum.Enum):
    living = "living"
    deceased = "deceased"
    unknown = "unknown"


RELATIONSHIPS = [
    "father", "mother", "brother", "sister", "son", "daughter",
    "grandfather", "grandmother", "uncle", "aunt", "other",
]


class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    relationship: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    living_status: Mapped[LivingStatus] = mapped_column(
        Enum(LivingStatus, native_enum=False, length=16), default=LivingStatus.unknown
    )
    relevant_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    conditions: Mapped[list["FamilyCondition"]] = orm_relationship(
        back_populates="member", cascade="all, delete-orphan"
    )


class FamilyRelationship(Base):
    """Edge between two family members of the same user (e.g., grandfather is father's father)."""
    __tablename__ = "family_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    member_a_id: Mapped[int] = mapped_column(ForeignKey("family_members.id", ondelete="CASCADE"), nullable=False)
    member_b_id: Mapped[int] = mapped_column(ForeignKey("family_members.id", ondelete="CASCADE"), nullable=False)
    relation_of_a_to_b: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FamilyCondition(Base):
    __tablename__ = "family_conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("family_members.id", ondelete="CASCADE"), index=True, nullable=False)
    condition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("conditions.id", ondelete="SET NULL"), nullable=True)
    condition_name: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnosis_age: Mapped[Optional[int]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    member: Mapped[FamilyMember] = orm_relationship(back_populates="conditions")
