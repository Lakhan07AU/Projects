"""Domain enumerations shared across models, schemas and services."""
from enum import Enum


class Role(str, Enum):
    CITIZEN = "CITIZEN"
    GOVERNMENT_OFFICIAL = "GOVERNMENT_OFFICIAL"
    ADMIN = "ADMIN"
    REPAIR_TEAM = "REPAIR_TEAM"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PotholeStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    AI_ANALYZED = "AI_ANALYZED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    PRIORITIZED = "PRIORITIZED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CITIZEN_VERIFICATION = "CITIZEN_VERIFICATION"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


# Allowed status transitions (validated by the repair workflow service).
STATUS_TRANSITIONS: dict[PotholeStatus, set[PotholeStatus]] = {
    PotholeStatus.SUBMITTED: {PotholeStatus.AI_ANALYZED, PotholeStatus.PENDING_VERIFICATION},
    PotholeStatus.AI_ANALYZED: {PotholeStatus.PENDING_VERIFICATION},
    PotholeStatus.PENDING_VERIFICATION: {PotholeStatus.VERIFIED, PotholeStatus.REJECTED},
    PotholeStatus.VERIFIED: {PotholeStatus.PRIORITIZED, PotholeStatus.PENDING_VERIFICATION},
    PotholeStatus.PRIORITIZED: {PotholeStatus.ASSIGNED, PotholeStatus.PENDING_VERIFICATION},
    PotholeStatus.ASSIGNED: {PotholeStatus.IN_PROGRESS, PotholeStatus.PRIORITIZED},
    PotholeStatus.IN_PROGRESS: {PotholeStatus.COMPLETED},
    PotholeStatus.COMPLETED: {PotholeStatus.CITIZEN_VERIFICATION},
    PotholeStatus.CITIZEN_VERIFICATION: {PotholeStatus.CLOSED, PotholeStatus.IN_PROGRESS},
    PotholeStatus.CLOSED: set(),
    PotholeStatus.REJECTED: set(),
}


class VerificationResult(str, Enum):
    REPAIRED = "REPAIRED"
    NOT_REPAIRED = "NOT_REPAIRED"
    PARTIAL = "PARTIAL"


class NotifType(str, Enum):
    SYSTEM = "SYSTEM"
    COMPLAINT = "COMPLAINT"
    REPAIR = "REPAIR"
    CRITICAL = "CRITICAL"
    DEADLINE = "DEADLINE"
