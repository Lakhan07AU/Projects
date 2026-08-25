"""Request/response schemas."""
from datetime import date as Date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# ---------- Auth ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class RefreshIn(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    role: str


# ---------- Profile ----------
class ProfileIn(BaseModel):
    date_of_birth: Optional[Date] = None
    sex: Optional[str] = Field(None, max_length=16)
    height_cm: Optional[float] = Field(None, gt=0, lt=300)
    weight_kg: Optional[float] = Field(None, gt=0, lt=700)
    blood_group: Optional[str] = Field(None, max_length=8)
    allergies: Optional[str] = None
    diet_preferences: Optional[str] = Field(None, max_length=64)
    exercise_preferences: Optional[str] = None
    emergency_information: Optional[str] = None


class ProfileOut(ProfileIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    age: Optional[int] = None
    bmi: Optional[float] = None


# ---------- Conditions / medications ----------
class ConditionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class UserConditionIn(BaseModel):
    condition_name: str = Field(max_length=255)
    diagnosed_year: Optional[int] = Field(None, ge=1900, le=2100)
    status: str = Field("active", pattern="^(active|resolved|monitoring)$")
    notes: Optional[str] = None


class UserConditionOut(UserConditionIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MedicationIn(BaseModel):
    name: str = Field(max_length=255)
    dosage: Optional[str] = Field(None, max_length=128)
    frequency: Optional[str] = Field(None, max_length=128)
    status: str = Field("active", pattern="^(active|stopped)$")
    started_on: Optional[str] = Field(None, max_length=32)
    notes: Optional[str] = None


class MedicationOut(MedicationIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Family ----------
class FamilyMemberIn(BaseModel):
    relationship: str = Field(pattern="^(father|mother|brother|sister|son|daughter|grandfather|grandmother|uncle|aunt|other)$")
    name: str = Field(max_length=255)
    date_of_birth: Optional[Date] = None
    living_status: str = Field("unknown", pattern="^(living|deceased|unknown)$")
    relevant_notes: Optional[str] = None


class FamilyConditionIn(BaseModel):
    condition_name: str = Field(max_length=255)
    diagnosis_age: Optional[int] = Field(None, ge=0, le=120)
    notes: Optional[str] = None


class FamilyConditionOut(FamilyConditionIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FamilyMemberOut(FamilyMemberIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    conditions: list[FamilyConditionOut] = []


# ---------- Reports ----------
class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    file_name: str
    mime_type: str
    file_size: int
    category: str
    report_date: Optional[datetime] = None
    laboratory: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    analysis_summary: Optional[str] = None
    created_at: datetime


class EntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    test_name: str
    value: float
    unit: Optional[str]
    reference_low: Optional[float]
    reference_high: Optional[float]
    abnormal_flag: bool
    confidence: float
    page_number: Optional[int]
    source_text: Optional[str]


class EntityPatchIn(BaseModel):
    """User corrections to extracted values — provenance is preserved."""
    value: float | None = None
    unit: Optional[str] = None
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None


class AnalysisOut(BaseModel):
    report: ReportOut
    entities: list[EntityOut]
    comparison: dict | None = None


# ---------- Metrics ----------
KNOWN_METRIC_KEYS = [
    "weight", "height", "bmi", "blood_pressure", "heart_rate", "blood_glucose",
    "hba1c", "cholesterol_total", "cholesterol_ldl", "cholesterol_hdl",
    "triglycerides", "sleep_hours", "exercise_minutes", "steps",
    "blood_glucose_fasting", "hemoglobin", "tsh", "creatinine",
]

class MetricValueIn(BaseModel):
    metric_key: str
    value: float = Field(gt=-1e9, lt=1e9)
    secondary_value: Optional[float] = None  # diastolic for blood_pressure
    unit: Optional[str] = Field(None, max_length=32)
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None


class MetricValueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    metric_key: str
    value: float
    secondary_value: Optional[float]
    unit: Optional[str]
    recorded_at: datetime
    source: str


# ---------- Doctors ----------
class DoctorIn(BaseModel):
    doctor_name: str = Field(max_length=255)
    specialty: Optional[str] = Field(None, max_length=128)
    clinic: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=32)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_family_doctor: bool = False


class DoctorOut(DoctorIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: Optional[str] = None


# ---------- Emergency contacts ----------
class EmergencyContactIn(BaseModel):
    name: str = Field(max_length=255)
    relationship: str = Field("family", pattern="^(family|friend|neighbour|doctor|other)$")
    phone: str = Field(max_length=32)
    priority: int = Field(1, ge=1, le=99)
    notes: Optional[str] = None


class EmergencyContactOut(EmergencyContactIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Reminders ----------
class ReminderIn(BaseModel):
    type: str = Field("general", max_length=32)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    due_at: datetime
    recurrence: str = Field("none", pattern="^(none|daily|weekly|monthly)$")


class ReminderUpdateIn(BaseModel):
    status: str | None = Field(None, pattern="^(open|done|cancelled)$")
    due_at: datetime | None = None


class ReminderOut(ReminderIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    source: str


# ---------- Lifestyle ----------
class LifestyleProfileIn(BaseModel):
    activity_level: Optional[str] = Field(None, pattern="^(sedentary|light|moderate|active|athlete)$")
    sleep_goal_hours: Optional[float] = Field(None, ge=3, le=14)
    diet_type: Optional[str] = Field(None, pattern="^(vegetarian|vegan|eggetarian|non_vegetarian|other)$")
    goal: Optional[str] = Field(None, pattern="^(maintain|lose_weight|gain_muscle|improve_fitness)$")
    smoking_status: Optional[str] = None
    alcohol_frequency: Optional[str] = None
    stress_level: Optional[str] = None


class LifestyleProfileOut(LifestyleProfileIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ExerciseLogIn(BaseModel):
    activity: str = Field(max_length=128)
    duration_minutes: int = Field(ge=1, le=1000)
    intensity: Optional[str] = Field(None, pattern="^(light|moderate|intense)$")
    performed_on: Date
    notes: Optional[str] = None


class ExerciseLogOut(ExerciseLogIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SleepLogIn(BaseModel):
    hours: float = Field(ge=0, le=24)
    quality: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")
    logged_on: Date
    notes: Optional[str] = None


class SleepLogOut(SleepLogIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Timeline / recommendations ----------
class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_type: str
    event_date: datetime
    title: str
    description: Optional[str]
    source: str
    related_entity_type: Optional[str]
    related_entity_id: Optional[int]


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kind: str
    topic: str
    reason: Optional[str]
    guidance: Optional[str]
    source_key: Optional[str]
    priority: str
    confidence: Optional[float]
    created_at: datetime


# ---------- Assistant ----------
class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: str
    content: str
    safety_filtered: bool
    created_at: datetime


# ---------- Doctor & Specialist section ----------
class SpecialtyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    key: str
    name: str
    description: Optional[str] = None


class SymptomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    key: str
    name: str
    category: Optional[str] = None


class UserSymptomIn(BaseModel):
    symptom_id: Optional[int] = None
    symptom_name: Optional[str] = Field(None, max_length=255)
    duration_text: Optional[str] = Field(None, max_length=64)
    severity: str = Field("moderate", pattern="^(mild|moderate|severe)$")
    notes: Optional[str] = None

    @model_validator(mode="after")
    def require_symptom(self):
        if not self.symptom_id and not (self.symptom_name or "").strip():
            raise ValueError("symptom_id or symptom_name is required")
        return self


class UserSymptomUpdateIn(BaseModel):
    duration_text: Optional[str] = Field(None, max_length=64)
    severity: Optional[str] = Field(None, pattern="^(mild|moderate|severe)$")
    notes: Optional[str] = None


class UserSymptomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    symptom_id: Optional[int]
    symptom_name: str
    duration_text: Optional[str]
    severity: str
    notes: Optional[str]
    created_at: datetime


class SpecialistRecommendationOut(BaseModel):
    id: int
    specialty_id: Optional[int]
    specialty_name: str
    relevance: str
    reason: str
    source_rules: list[str] = []
    status: str
    created_at: datetime


class AnalyzeResponse(BaseModel):
    red_flag: bool
    matched_indicator: Optional[str] = None
    message: Optional[str] = None
    insufficient_info: bool = False
    recommendations: list[SpecialistRecommendationOut] = []
    family_doctor: Optional[dict] = None


class RemindMeIn(BaseModel):
    when: str = Field(pattern="^(tomorrow|in_3_days|next_week|custom)$")
    custom_at: Optional[datetime] = None


# ---------- Consents ----------
class ConsentIn(BaseModel):
    consent_type: str
    granted: bool


class ConsentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    consent_type: str
    granted: bool
    version: str
    granted_at: datetime
