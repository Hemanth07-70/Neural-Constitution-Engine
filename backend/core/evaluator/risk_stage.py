"""Stage 2: Assesses risk from matched rules."""

from backend.core.constitution.constitution import Constitution
from backend.core.domain.enums import RiskLevel
from backend.core.domain.request import DecisionRequest
from backend.core.domain.risk import RiskAssessment, RiskFactor
from backend.core.rules.context import EvaluationContext

from .stages import PipelineData, PipelineStage


class RiskStage(PipelineStage):
    """Aggregates matched rules into a RiskAssessment."""

    def execute(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        context: EvaluationContext,
        data: PipelineData,
    ) -> PipelineData:
        if not data.matches:
            risk = RiskAssessment(level=RiskLevel.INFORMATIONAL, determined_by="aggregate")
            return data.replace(risk=risk)

        factors = []
        highest_level = RiskLevel.INFORMATIONAL

        level_order = {
            RiskLevel.INFORMATIONAL: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }

        for match in data.matches:
            sev_str = match.rule.severity or "informational"
            try:
                level = RiskLevel(sev_str.lower())
            except ValueError:
                level = RiskLevel.INFORMATIONAL

            factors.append(
                RiskFactor(
                    rule_id=match.rule.id,
                    category=match.rule.category or "operational",
                    severity=level,
                    note=match.error_note,
                )
            )
            if level_order[level] > level_order[highest_level]:
                highest_level = level

        risk = RiskAssessment(level=highest_level, determined_by="aggregate", factors=tuple(factors))
        return data.replace(risk=risk)
