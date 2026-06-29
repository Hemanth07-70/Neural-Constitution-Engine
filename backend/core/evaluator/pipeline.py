"""The Deterministic Evaluation Pipeline."""

from backend.core.constitution.constitution import Constitution
from backend.core.domain.audit import AuditRecord
from backend.core.domain.explanation import Explanation
from backend.core.domain.request import DecisionRequest
from backend.core.domain.result import EvaluationResult
from backend.core.rules.context import EvaluationContext

from .audit_stage import AuditStage
from .exceptions import FailClosedError
from .explanation_stage import ExplanationStage
from .matcher_stage import MatcherStage
from .resolver_stage import ResolverStage
from .risk_stage import RiskStage
from .stages import PipelineData, PipelineStage


class EvaluationPipeline:
    """Orchestrates the evaluation of a request against a constitution."""

    def __init__(self, stages: list[PipelineStage] | None = None) -> None:
        if stages is None:
            self.stages = [
                MatcherStage(),
                RiskStage(),
                ResolverStage(),
                ExplanationStage(),
                AuditStage(),
            ]
        else:
            self.stages = stages

    def evaluate(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        registry: getattr(__import__("typing"), "Any") = None
    ) -> tuple[EvaluationResult, Explanation, AuditRecord]:
        """Execute the pipeline sequentially."""
        
        context = EvaluationContext(request=request, registry=registry)
        data = PipelineData()

        try:
            for stage in self.stages:
                data = stage.execute(request, constitution, context, data)
                
            assert data.result is not None
            assert data.explanation is not None
            assert data.audit is not None
            return data.result, data.explanation, data.audit
            
        except Exception as e:
            raise FailClosedError(f"Pipeline failed closed due to error: {e}") from e
