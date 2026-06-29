"""Stage 1: Matches rules against the request."""

from backend.core.constitution.constitution import Constitution
from backend.core.domain.request import DecisionRequest
from backend.core.rules.context import EvaluationContext, MatchResult
from .stages import PipelineData, PipelineStage


class MatcherStage(PipelineStage):
    """Evaluates all constitution rules against the request.
    
    Since plugins are not fully implemented, this stage delegates to a stubbed Matcher
    if provided in the registry, or provides simple deterministic matching logic.
    """

    def execute(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        context: EvaluationContext,
        data: PipelineData,
    ) -> PipelineData:
        matches = []
        for rule in constitution.rules:
            if not rule.enabled:
                continue
            
            is_match = False
            if not rule.condition:
                is_match = True
            else:
                # Basic literal match stub for testing
                field_path = rule.condition.get("field")
                op = rule.condition.get("op")
                value = rule.condition.get("value")
                if field_path == "action.type" and op == "equals":
                    is_match = (request.action.type == value)

            if is_match:
                matches.append(MatchResult(matched=True, rule=rule))
                
        return data.replace(matches=tuple(matches))
