"""All SQLAlchemy models. Importing this package registers every table with Base.metadata."""
from app.models.user import User, UserProfile
from app.models.family import FamilyCondition, FamilyMember, FamilyRelationship, LivingStatus
from app.models.clinical import Condition, Medication, UserCondition
from app.models.metric import HealthMetric, HealthMetricValue
from app.models.report import DocumentProcessingJob, MedicalEntity, MedicalReport, ReportStatus
from app.models.care import (
    ConditionSpecialtyMap,
    Doctor,
    EmergencyAlert,
    EmergencyContact,
    Hospital,
    Notification,
    Reminder,
    ReminderRecurrence,
    SpecialistRecommendation,
    Specialty,
    Symptom,
    SymptomSeverity,
    SymptomSpecialtyMap,
    UserSymptom,
)
from app.models.lifestyle import DietLog, ExerciseLog, LifestyleProfile, SleepLog
from app.models.intelligence import (
    ClinicalRule,
    ClinicalSource,
    HealthTimelineEvent,
    Priority,
    Recommendation,
    RecommendationKind,
    TimelineEventType,
)
from app.models.ai import (
    AIMessage,
    AIConversation,
    AuditLog,
    Consent,
    RefreshSession,
)

__all__ = [
    "User", "UserProfile",
    "FamilyMember", "FamilyRelationship", "FamilyCondition", "LivingStatus",
    "Condition", "UserCondition", "Medication",
    "HealthMetric", "HealthMetricValue",
    "MedicalReport", "MedicalEntity", "DocumentProcessingJob", "ReportStatus",
    "Doctor", "EmergencyContact", "EmergencyAlert", "Hospital", "Reminder", "ReminderRecurrence", "Notification",
    "Specialty", "Symptom", "SymptomSpecialtyMap", "ConditionSpecialtyMap",
    "UserSymptom", "SymptomSeverity", "SpecialistRecommendation",
    "LifestyleProfile", "ExerciseLog", "DietLog", "SleepLog",
    "ClinicalSource", "ClinicalRule", "Recommendation", "RecommendationKind", "Priority",
    "HealthTimelineEvent", "TimelineEventType",
    "AIConversation", "AIMessage", "Consent", "AuditLog", "RefreshSession",
]
