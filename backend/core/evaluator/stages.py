"""Pipeline abstraction and common state."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from backend.core.constitution.constitution import Constitution
from backend.core.domain.audit import AuditRecord
from backend.core.domain.explanation import Explanation
from backend.core.domain.request import DecisionRequest
from backend.core.domain.result import EvaluationResult
from backend.core.domain.risk import RiskAssessment
from backend.core.rules.context import EvaluationContext, MatchResult, ResolvedVerdict


@dataclass(slots=True, frozen=True)
class PipelineData:
    """Immutable data passed and enriched across pipeline stages.

    Each stage creates a new copy with its specific output populated.
    """

    matches: tuple[MatchResult, ...] = field(default_factory=tuple)
    risk: RiskAssessment | None = None
    verdict: ResolvedVerdict | None = None
    result: EvaluationResult | None = None
    explanation: Explanation | None = None
    audit: AuditRecord | None = None

    def replace(self, **changes: Any) -> "PipelineData":
        import dataclasses

        return dataclasses.replace(self, **changes)


class PipelineStage(ABC):
    """Base interface for a stage in the evaluation pipeline.

    Stages must be deterministic, pure, and not mutate shared state.
    """

    @abstractmethod
    def execute(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        context: EvaluationContext,
        data: PipelineData,
    ) -> PipelineData:
        """Execute the stage and return a new PipelineData with enriched output."""
        pass
