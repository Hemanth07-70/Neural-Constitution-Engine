"""The public Engine facade."""

from pathlib import Path

from backend.core.constitution.constitution import Constitution
from backend.core.constitution.loader import ConstitutionLoader
from backend.core.evaluator.pipeline import EvaluationPipeline
from backend.core.planner.validator import PlanValidator
from backend.core.plugins.manager import PluginManager

from .config import EngineConfig
from .exceptions import ConstitutionValidationError, EvaluationError
from .types import AuditRecord, DecisionRequest, ExecutionPlan, PlanValidationResult


class Engine:
    """The Neural Constitution Engine facade.

    Do not instantiate this directly; use EngineBuilder or Engine.load().
    """

    def __init__(
        self,
        config: EngineConfig,
        constitution: Constitution,
        plugin_manager: PluginManager,
        pipeline: EvaluationPipeline,
    ) -> None:
        """Internal constructor. Use EngineBuilder.build() instead."""
        self._config = config
        self._constitution = constitution
        self._plugin_manager = plugin_manager
        self._pipeline = pipeline

    @classmethod
    def load(cls, path: str | Path) -> "Engine":
        """Load an engine instance with a default configuration and the given constitution."""
        from .builder import EngineBuilder

        return EngineBuilder().build(path)

    def evaluate(self, request: DecisionRequest) -> AuditRecord:
        """Evaluate a single decision request against the loaded constitution.

        Args:
            request: The decision request to evaluate.

        Returns:
            An immutable AuditRecord detailing the decision and rationale.

        Raises:
            EvaluationError: If the engine fails-closed during evaluation.
        """
        try:
            _, _, audit = self._pipeline.evaluate(
                request=request, constitution=self._constitution, registry=self._plugin_manager
            )
            return audit
        except Exception as e:
            raise EvaluationError(f"Evaluation failed: {e}") from e

    def evaluate_plan(self, plan: ExecutionPlan) -> PlanValidationResult:
        """Validate an execution plan topologically and structurally.

        Args:
            plan: The execution plan DAG.

        Returns:
            A PlanValidationResult detailing the structural integrity and topological order.
        """
        result = PlanValidator.validate(plan)
        if not result.is_valid:
            return result

        from dataclasses import replace

        from .types import VerdictAction

        node_results = {}
        failed_node_id = None
        is_valid = True

        for node in result.topological_order:
            audit = self.evaluate(node.request)
            node_results[node.id] = audit
            if audit.result.action == VerdictAction.BLOCK:
                failed_node_id = node.id
                is_valid = False
                break

        return replace(result, is_valid=is_valid, failed_node_id=failed_node_id, node_results=node_results)

    @classmethod
    def validate_constitution(cls, path: str | Path) -> bool:
        """Validate a constitution file structurally.

        Args:
            path: Path to the JSON/YAML constitution file.

        Returns:
            True if valid.

        Raises:
            ConstitutionValidationError: If the constitution is invalid.
        """
        try:
            ConstitutionLoader().load_file(path)
            return True
        except Exception as e:
            raise ConstitutionValidationError(f"Invalid constitution: {e}") from e

    @staticmethod
    def version() -> str:
        """Return the current engine version."""
        return "0.1.0-alpha"
