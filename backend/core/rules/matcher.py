"""Rule matching interface."""

from abc import ABC, abstractmethod

from backend.core.constitution.rule import Rule
from .context import EvaluationContext, MatchResult


class RuleMatcher(ABC):
    """Interface for evaluating a rule's condition against a request.

    The matcher is responsible for processing a rule's condition tree
    (including boolean logic like `all`, `any`, `not`) and delegating
    to registered evaluators if necessary.

    Invariants:
        - Deterministic matching.
        - Fail-closed: Any unrecoverable error during matching must result
          in a match with an error_note attached (fail-closed behavior).
    """

    @abstractmethod
    def match(self, rule: Rule, context: EvaluationContext) -> MatchResult:
        """Determine if a rule applies to the given evaluation context.

        Args:
            rule: The Rule to match.
            context: The EvaluationContext containing the DecisionRequest and registry.

        Returns:
            A MatchResult indicating whether the rule matched, along with any
            findings or error notes.
        """
        pass
