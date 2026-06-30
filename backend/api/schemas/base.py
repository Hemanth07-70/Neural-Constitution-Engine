"""Base schema types and shared models for the API."""

from enum import StrEnum

from pydantic import BaseModel


class ActorType(StrEnum):
    """Types of actors recognized by the system."""

    AGENT = "agent"
    HUMAN = "human"
    SYSTEM = "system"


class RiskLevel(StrEnum):
    """The severity level of a risk factor."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class Scope(StrEnum):
    """The authority scope of a rule."""

    GLOBAL = "global"
    PROJECT = "project"
    TEAM = "team"
    PERSONAL = "personal"


class VerdictAction(StrEnum):
    """The conclusive action to take."""

    ALLOW = "allow"
    WARN = "warn"
    REWRITE = "rewrite"
    REQUEST_HUMAN_APPROVAL = "request_human_approval"
    ESCALATE = "escalate"
    BLOCK = "block"


class EnvironmentName(StrEnum):
    """Standard deployment environments."""

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TEST = "test"


class BaseSchema(BaseModel):
    """Base Pydantic schema for all API models."""

    class Config:
        populate_by_name = True
        extra = "forbid"
