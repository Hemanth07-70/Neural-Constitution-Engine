"""Stage 3: Resolves rule conflicts."""

from backend.core.constitution.constitution import Constitution
from backend.core.domain.enums import VerdictAction
from backend.core.domain.request import DecisionRequest
from backend.core.rules.context import EvaluationContext, ResolvedVerdict
from backend.core.domain.explanation import OverriddenContender
from backend.core.domain.enums import Scope
from .stages import PipelineData, PipelineStage


class ResolverStage(PipelineStage):
    """Applies conflict resolution to select the winning rule."""

    def execute(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        context: EvaluationContext,
        data: PipelineData,
    ) -> PipelineData:
        if not data.matches:
            default_action = VerdictAction.BLOCK
            if constitution.resolution:
                try:
                    default_action = VerdictAction(constitution.resolution.default_verdict)
                except ValueError:
                    pass
            from backend.core.constitution.rule import Rule, RuleAction
            fallback_rule = Rule(
                id="SYS-FALLBACK",
                condition={},
                action=RuleAction(type=default_action.value, message="No rules matched.")
            )
            verdict = ResolvedVerdict(winning_rule=fallback_rule)
            return data.replace(verdict=verdict)

        action_order = {
            VerdictAction.BLOCK: 5,
            VerdictAction.ESCALATE: 4,
            VerdictAction.REQUEST_HUMAN_APPROVAL: 3,
            VerdictAction.REWRITE: 2,
            VerdictAction.WARN: 1,
            VerdictAction.ALLOW: 0,
        }

        def sort_key(match):
            action_str = match.rule.action.type.lower() if match.rule.action else "allow"
            try:
                action_enum = VerdictAction(action_str)
            except ValueError:
                action_enum = VerdictAction.BLOCK
                
            return (
                action_order.get(action_enum, 5),
                match.rule.id
            )

        sorted_matches = sorted(data.matches, key=sort_key, reverse=True)
        winner = sorted_matches[0]
        
        contenders = []
        for match in sorted_matches[1:]:
            action_str = match.rule.action.type.lower() if match.rule.action else "allow"
            try:
                action_enum = VerdictAction(action_str)
            except ValueError:
                action_enum = VerdictAction.BLOCK
            
            contenders.append(OverriddenContender(
                id=match.rule.id,
                scope=Scope.PROJECT, # Default simulation
                action=action_enum,
                reason="lower authority"
            ))
            
        verdict = ResolvedVerdict(
            winning_rule=winner.rule,
            overridden_contenders=tuple(contenders)
        )
        return data.replace(verdict=verdict)
