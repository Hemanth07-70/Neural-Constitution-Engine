"""Evaluator plugin interfaces."""

from abc import ABC, abstractmethod
from typing import Any

from backend.core.domain.request import DecisionRequest


class RuleEvaluator(ABC):
    """Interface for custom condition evaluators (plugins).

    An evaluator is conceptually a pure function: given a normalized proposal
    and declared parameters, it returns a deterministic boolean indicating
    whether the rule matches, along with an optional structured finding.

    Invariants:
        - Pure & deterministic: Identical inputs must yield identical outputs.
        - Side-effect free: Must not perform external I/O on the hot path.
        - Sandboxed & bounded: A failing evaluator yields a fail-closed match.
    """

    @abstractmethod
    def evaluate(self, request: DecisionRequest, params: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        """Evaluate the condition against the request.

        Args:
            request: The normalized DecisionRequest.
            params: Parameters provided in the rule's condition block.

        Returns:
            A tuple of (matched: bool, findings: dict | None).
        """
        pass
