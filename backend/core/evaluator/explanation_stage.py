"""Stage 4: Produces the Decision Result and Explanation."""

import uuid
from datetime import datetime, timezone

from backend.core.constitution.constitution import Constitution
from backend.core.domain.enums import ResultStatus, VerdictAction, RiskLevel, Scope, ResolutionStrategy
from backend.core.domain.explanation import Explanation, Verdict, DeterminingRule, Resolution
from backend.core.domain.request import DecisionRequest
from backend.core.domain.result import EvaluationResult
from backend.core.rules.context import EvaluationContext
from .stages import PipelineData, PipelineStage


class ExplanationStage(PipelineStage):
    """Constructs the Result and Explanation from the resolved verdict."""

    def execute(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        context: EvaluationContext,
        data: PipelineData,
    ) -> PipelineData:
        assert data.risk is not None
        assert data.verdict is not None

        result_id = uuid.uuid7() if hasattr(uuid, "uuid7") else uuid.uuid4()
        
        action_str = data.verdict.winning_rule.action.type.lower()
        try:
            action = VerdictAction(action_str)
        except ValueError:
            action = VerdictAction.BLOCK

        status = ResultStatus.PENDING if action in (VerdictAction.REQUEST_HUMAN_APPROVAL, VerdictAction.ESCALATE) else ResultStatus.FINAL

        result = EvaluationResult(
            api_version="nce/v1",
            id=result_id,
            request_id=request.id,
            action=action,
            risk=data.risk,
            status=status,
            decided_at=datetime.now(timezone.utc),
            determining_rule_id=data.verdict.winning_rule.id,
            warnings=tuple(context.warnings)
        )

        severity_str = data.verdict.winning_rule.severity or "informational"
        try:
            severity = RiskLevel(severity_str.lower())
        except ValueError:
            severity = RiskLevel.INFORMATIONAL

        determining_rule = DeterminingRule(
            id=data.verdict.winning_rule.id,
            scope=Scope.PROJECT,
            category=data.verdict.winning_rule.category or "operational",
            severity=severity,
            principle="P-SYS",
            statement="System determining rule.",
            message=data.verdict.winning_rule.action.message or ""
        )
        
        resolution = Resolution(
            strategy=ResolutionStrategy.MOST_RESTRICTIVE_WINS,
            decided_by="action-authority",
            overridden_contenders=data.verdict.overridden_contenders
        )
        
        explanation = Explanation(
            decision_id=result_id,
            verdict=Verdict(action=action, risk_level=data.risk.level),
            determining_rule=determining_rule,
            resolution=resolution
        )
        
        return data.replace(result=result, explanation=explanation)
