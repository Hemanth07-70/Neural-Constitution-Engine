"""Adapters for translating between Pydantic schemas and SDK types."""

from typing import Any

from backend.api.schemas import evaluate as eval_schemas
from backend.api.schemas import plans as plan_schemas
from backend.api.schemas.base import ActorType, EnvironmentName, RiskLevel, Scope, VerdictAction
from backend.sdk import types as sdk_types


def to_sdk_actor(schema: eval_schemas.ActorSchema) -> sdk_types.Actor:
    from backend.core.domain.enums import ActorType as SDKActorType

    return sdk_types.Actor(
        id=schema.id,
        type=SDKActorType(schema.type.value),
        roles=schema.roles,
        attributes=dict(schema.attributes),
    )


def to_sdk_environment(schema: eval_schemas.EnvironmentSchema) -> sdk_types.Environment:
    from backend.core.domain.enums import EnvironmentName as SDKEnvironmentName

    return sdk_types.Environment(
        name=SDKEnvironmentName(schema.name.value),
        timestamp=schema.timestamp,
    )


def to_sdk_decision_context(schema: eval_schemas.DecisionContextSchema) -> sdk_types.DecisionContext:
    return sdk_types.DecisionContext(
        constitution_id=schema.constitution_id,
        constitution_version=schema.constitution_version,
        environment=to_sdk_environment(schema.environment),
        correlation_id=schema.correlation_id,
    )


def to_sdk_action(schema: eval_schemas.ActionSchema) -> sdk_types.Action:
    return sdk_types.Action(
        type=schema.type,
        params=dict(schema.params),
    )


def to_sdk_decision_request(schema: eval_schemas.DecisionRequestSchema) -> sdk_types.DecisionRequest:
    return sdk_types.DecisionRequest(
        api_version=schema.api_version,
        id=schema.id,
        actor=to_sdk_actor(schema.actor),
        action=to_sdk_action(schema.action),
        context=to_sdk_decision_context(schema.context),
        submitted_at=schema.submitted_at,
    )


def from_sdk_risk_assessment(sdk_risk: Any) -> eval_schemas.RiskAssessmentSchema:
    factors = []
    for f in getattr(sdk_risk, "factors", []):
        factors.append(
            eval_schemas.RiskFactorSchema(
                rule_id=f.rule_id,
                category=f.category,
                severity=RiskLevel(f.severity.value),
                note=f.note,
            )
        )
    return eval_schemas.RiskAssessmentSchema(
        level=RiskLevel(sdk_risk.level.value),
        factors=tuple(factors),
    )


def from_sdk_evaluation_result(sdk_result: sdk_types.EvaluationResult) -> eval_schemas.EvaluationResultSchema:
    return eval_schemas.EvaluationResultSchema(
        api_version=sdk_result.api_version,
        id=sdk_result.id,
        request_id=sdk_result.request_id,
        action=VerdictAction(sdk_result.action.value),
        risk=from_sdk_risk_assessment(sdk_result.risk),
        status=sdk_result.status.value if hasattr(sdk_result.status, "value") else str(sdk_result.status),
        decided_at=sdk_result.decided_at,
        determining_rule_id=sdk_result.determining_rule_id or "",
        warnings=sdk_result.warnings,
    )


def from_sdk_determining_rule(sdk_rule: Any) -> eval_schemas.DeterminingRuleSchema:
    return eval_schemas.DeterminingRuleSchema(
        id=sdk_rule.id,
        scope=Scope(sdk_rule.scope.value),
        category=sdk_rule.category,
        severity=RiskLevel(sdk_rule.severity.value),
        principle=sdk_rule.principle,
        statement=sdk_rule.statement,
        message=sdk_rule.message,
    )


def from_sdk_resolution(sdk_res: Any) -> eval_schemas.ResolutionSchema:
    contenders = []
    for c in sdk_res.overridden_contenders:
        contenders.append(
            eval_schemas.OverriddenContenderSchema(
                id=c.id,
                scope=Scope(c.scope.value),
                action=VerdictAction(c.action.value),
                reason=c.reason,
            )
        )
    return eval_schemas.ResolutionSchema(
        strategy=sdk_res.strategy.value if hasattr(sdk_res.strategy, "value") else str(sdk_res.strategy),
        decided_by=sdk_res.decided_by,
        overridden_contenders=tuple(contenders),
    )


def from_sdk_explanation(sdk_expl: Any) -> eval_schemas.ExplanationSchema:
    return eval_schemas.ExplanationSchema(
        decision_id=sdk_expl.decision_id,
        verdict=eval_schemas.VerdictSchema(
            action=VerdictAction(sdk_expl.verdict.action.value),
            risk_level=RiskLevel(sdk_expl.verdict.risk_level.value),
        ),
        determining_rule=from_sdk_determining_rule(sdk_expl.determining_rule),
        resolution=from_sdk_resolution(sdk_expl.resolution),
    )


def from_sdk_audit_record(sdk_audit: sdk_types.AuditRecord) -> eval_schemas.AuditRecordSchema:
    return eval_schemas.AuditRecordSchema(
        id=str(sdk_audit.id),
        content_hash=sdk_audit.content_hash,
        recorded_at=sdk_audit.recorded_at,
        request=eval_schemas.DecisionRequestSchema(
            api_version=sdk_audit.request.api_version,
            id=sdk_audit.request.id,
            actor=eval_schemas.ActorSchema(
                id=sdk_audit.request.actor.id,
                type=ActorType(sdk_audit.request.actor.type.value),
                roles=sdk_audit.request.actor.roles,
                attributes=dict(sdk_audit.request.actor.attributes),
            ),
            action=eval_schemas.ActionSchema(
                type=sdk_audit.request.action.type,
                params=dict(sdk_audit.request.action.params),
            ),
            context=eval_schemas.DecisionContextSchema(
                constitution_id=sdk_audit.request.context.constitution_id,
                constitution_version=sdk_audit.request.context.constitution_version,
                environment=eval_schemas.EnvironmentSchema(
                    name=EnvironmentName(sdk_audit.request.context.environment.name.value),
                    timestamp=sdk_audit.request.context.environment.timestamp,
                ),
                correlation_id=sdk_audit.request.context.correlation_id,
            ),
            submitted_at=sdk_audit.request.submitted_at,
        ),
        result=from_sdk_evaluation_result(sdk_audit.result),
        explanation=from_sdk_explanation(sdk_audit.explanation),
    )


def to_sdk_plan_metadata(schema: plan_schemas.PlanMetadataSchema) -> sdk_types.PlanMetadata:
    return sdk_types.PlanMetadata(
        id=schema.id,
        creator=schema.creator,
        created_at=schema.created_at,
        goal_description=schema.goal_description,
        extensions=dict(schema.extensions),
    )


def to_sdk_plan_node(schema: plan_schemas.PlanNodeSchema) -> sdk_types.PlanNode:
    return sdk_types.PlanNode(
        id=schema.id,
        request=to_sdk_decision_request(schema.request),
        preconditions=schema.preconditions,
        postconditions=schema.postconditions,
        estimated_cost=dict(schema.estimated_cost) if schema.estimated_cost else None,
        human_approval_required=schema.human_approval_required,
        extensions=dict(schema.extensions),
    )


def to_sdk_plan_edge(schema: plan_schemas.PlanEdgeSchema) -> sdk_types.PlanEdge:
    return sdk_types.PlanEdge(
        source_id=schema.source_id,
        target_id=schema.target_id,
        condition=schema.condition,
        extensions=dict(schema.extensions),
    )


def to_sdk_execution_plan(schema: plan_schemas.ExecutionPlanSchema) -> sdk_types.ExecutionPlan:
    return sdk_types.ExecutionPlan(
        metadata=to_sdk_plan_metadata(schema.metadata),
        nodes=tuple(to_sdk_plan_node(n) for n in schema.nodes),
        edges=tuple(to_sdk_plan_edge(e) for e in schema.edges),
    )


def from_sdk_plan_validation_result(
    sdk_result: sdk_types.PlanValidationResult,
) -> plan_schemas.PlanValidationResultSchema:
    return plan_schemas.PlanValidationResultSchema(
        is_valid=sdk_result.is_valid,
        errors=sdk_result.errors,
        warnings=sdk_result.warnings,
        topological_order=tuple(node.id for node in sdk_result.topological_order),
        failed_node_id=sdk_result.failed_node_id,
        node_results={node_id: from_sdk_audit_record(audit) for node_id, audit in sdk_result.node_results.items()},
    )
