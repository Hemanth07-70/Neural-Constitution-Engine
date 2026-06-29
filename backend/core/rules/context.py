"""Context and result objects for rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.constitution.rule import Rule
from backend.core.domain.request import DecisionRequest


@dataclass(slots=True)
class EvaluationContext:
    """State and injected dependencies passed through the evaluation pipeline.

    This object holds intermediate evaluation state and references to dependencies
    like the RuleRegistry to ensure pure, side-effect-free execution.
    """
    request: DecisionRequest
    # We use 'Any' for the registry to avoid a circular dependency in type hints,
    # or it can be properly typed using TYPE_CHECKING.
    registry: Any
    warnings: list[str] = field(default_factory=list)
    applied_transforms: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class MatchResult:
    """The result of evaluating a rule's condition against a request."""
    matched: bool
    rule: Rule
    # Optional findings from a plugin evaluator to be included in the explanation
    findings: dict[str, Any] | None = None
    # If the evaluator failed closed, record the error note
    error_note: str | None = None


@dataclass(slots=True, frozen=True)
class ResolvedVerdict:
    """The final resolved verdict from the conflict resolver."""
    winning_rule: Rule
    # Information about why contenders lost
    overridden_contenders: tuple[dict[str, Any], ...] = field(default_factory=tuple)
