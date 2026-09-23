from enum import StrEnum


class SampleStatus(StrEnum):
    COLLECTED = "collected"
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    REJECTED = "rejected"


class ResultStatus(StrEnum):
    PRELIMINARY = "preliminary"
    AVAILABLE = "available"
    FLAGGED = "flagged"
    REVIEWED = "reviewed"


class QcStatus(StrEnum):
    ACCEPTED = "accepted"
    FLAGGED = "flagged"
    INVALID = "invalid"


class RuleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class AlertStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    CLOSED = "closed"


class AlertSeverity(StrEnum):
    INFORMATION = "information"
    REVIEW = "review"
    HIGH = "high"


class ValidationOutcome(StrEnum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DEFERRED = "deferred"


class AuditAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    REVIEWED = "reviewed"
    EXPORTED = "exported"
