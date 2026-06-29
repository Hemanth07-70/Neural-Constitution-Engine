"""Conflict resolution interface."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from .context import MatchResult, ResolvedVerdict


class RuleResolver(ABC):
    """Interface for resolving conflicts among multiple matched rules.

    When multiple rules match a single proposal, the engine must select exactly one
    winning action deterministically based on action authority, scope authority,
    severity, priority, and finally a lexical tiebreaker.

    Invariants:
        - Deterministic outcome.
        - Always resolves to exactly one winning rule if the input sequence is non-empty.
    """

    @abstractmethod
    def resolve(self, matches: Sequence[MatchResult]) -> ResolvedVerdict:
        """Resolve a set of matched rules into a single verdict.

        Args:
            matches: A sequence of MatchResults where matched == True.

        Returns:
            A ResolvedVerdict containing the winning rule and the overridden contenders.
        """
        pass
