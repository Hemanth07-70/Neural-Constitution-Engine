"""Pydantic schemas for the evaluation endpoints."""

import datetime
import uuid
from typing import Any

from pydantic import Field

from backend.api.schemas.base import ActorType, BaseSchema, EnvironmentName, RiskLevel, Scope, VerdictAction


class ActorSchema(BaseSchema):
    id: str = Field(..., description="Stable, globally unique URN")
    type: ActorType = Field(..., description="The kind of principal")
    roles: tuple[str, ...] = Field(default=(), description="Roles the actor holds")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Deployment-defined attributes")


class EnvironmentSchema(BaseSchema):
    name: EnvironmentName
    timestamp: datetime.datetime


class DecisionContextSchema(BaseSchema):
    constitution_id: str
    constitution_version: str
    environment: EnvironmentSchema
    correlation_id: uuid.UUID


class ActionSchema(BaseSchema):
    type: str
    params: dict[str, Any] = Field(default_factory=dict)


class DecisionRequestSchema(BaseSchema):
    api_version: str = Field(default="nce/v1")
    id: uuid.UUID
    actor: ActorSchema
    action: ActionSchema
    context: DecisionContextSchema
    submitted_at: datetime.datetime


class DeterminingRuleSchema(BaseSchema):
    id: str
    scope: Scope
    category: str
    severity: RiskLevel
    principle: str
    statement: str
    message: str


class OverriddenContenderSchema(BaseSchema):
    id: str
    scope: Scope
    action: VerdictAction
    reason: str


class ResolutionSchema(BaseSchema):
    strategy: str
    decided_by: str
    overridden_contenders: tuple[OverriddenContenderSchema, ...] = Field(default_factory=tuple)


class VerdictSchema(BaseSchema):
    action: VerdictAction
    risk_level: RiskLevel


class ExplanationSchema(BaseSchema):
    decision_id: uuid.UUID
    verdict: VerdictSchema
    determining_rule: DeterminingRuleSchema
    resolution: ResolutionSchema


class RiskFactorSchema(BaseSchema):
    rule_id: str
    category: str
    severity: RiskLevel
    note: str | None = None


class RiskAssessmentSchema(BaseSchema):
    level: RiskLevel
    factors: tuple[RiskFactorSchema, ...] = Field(default_factory=tuple)


class EvaluationResultSchema(BaseSchema):
    api_version: str
    id: uuid.UUID
    request_id: uuid.UUID
    action: VerdictAction
    risk: RiskAssessmentSchema
    status: str
    decided_at: datetime.datetime
    determining_rule_id: str
    warnings: tuple[str, ...] = Field(default_factory=tuple)


class AuditRecordSchema(BaseSchema):
    id: str
    content_hash: str
    recorded_at: datetime.datetime
    request: DecisionRequestSchema
    result: EvaluationResultSchema
    explanation: ExplanationSchema
