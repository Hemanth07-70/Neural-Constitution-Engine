"""Risk modelling: :class:`RiskFactor` and :class:`RiskAssessment`.

See ``docs/decision-model.md`` §2.8 and ``docs/constitution-engine.md`` §7. Risk
is *descriptive of policy* (how dangerous the proposal is); the *prescriptive*
outcome is the :class:`~core.domain.enums.VerdictAction` carried by the result.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .aliases import Category
from .enums import RiskLevel


@dataclass(slots=True, frozen=True)
class RiskFactor:
    """A single rule's contribution to an assessed risk.

    Required
        ``rule_id``: the contributing rule.
        ``category``: the rule's category (open vocabulary).
        ``severity``: the rule's severity.

    Optional
        ``note``: human-readable explanation of the contribution.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Aggregated by a :class:`RiskAssessment`.
    """

    rule_id: str
    category: Category
    severity: RiskLevel
    note: str | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RiskAssessment:
    """The engine's structured judgement of how dangerous a proposal is.

    Required
        ``level``: the overall assessed risk level.
        ``determined_by``: what set the level (e.g. a winning rule id, or the
        token ``aggregate``).

    Optional
        ``score``: an optional normalised quantitative signal in ``[0, 1]``.
        ``factors``: the per-rule contributions.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Produced from the matched-rule set; embedded in one
        :class:`~core.domain.result.EvaluationResult` and surfaced in the
        :class:`~core.domain.explanation.Explanation`.

    Invariants (documented, not enforced here)
        ``level`` equals the highest severity among contributing rules; ``score``,
        when present, is monotonic with ``level``.
    """

    level: RiskLevel
    determined_by: str
    score: float | None = None
    factors: tuple[RiskFactor, ...] = ()
    extensions: Mapping[str, object] = field(default_factory=dict)
