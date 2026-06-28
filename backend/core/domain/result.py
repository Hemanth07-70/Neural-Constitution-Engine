"""The verdict: :class:`EvaluationResult`.

See ``docs/decision-model.md`` §2.9. The single resolved action the engine
prescribes for a request, plus everything needed to act on and understand it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .action import Action
from .aliases import ApiVersion
from .enums import ResultStatus, VerdictAction
from .risk import RiskAssessment


@dataclass(slots=True, frozen=True)
class EvaluationResult:
    """The resolved verdict for one :class:`~core.domain.request.DecisionRequest`.

    Required
        ``api_version``: the Decision Model schema version.
        ``id``: unique result identifier.
        ``request_id``: the request that was evaluated.
        ``action``: the single resolved verdict action.
        ``risk``: the embedded risk judgement.
        ``status``: ``final``, or ``pending`` while awaiting a human.
        ``decided_at``: when the verdict was produced.

    Optional
        ``transformed_action``: the rewritten action — present **iff** ``action``
        is ``REWRITE``.
        ``warnings``: advisory notes attached to the verdict.
        ``determining_rule_id``: the rule that settled the outcome.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Belongs to one :class:`~core.domain.request.DecisionRequest`; embeds one
        :class:`~core.domain.risk.RiskAssessment`; is explained by one
        :class:`~core.domain.explanation.Explanation`; is sealed into one
        :class:`~core.domain.audit.AuditRecord`. A ``pending`` result is
        superseded by a new linked result when the human decides — never mutated.

    Invariants (documented, not enforced here)
        ``transformed_action`` is present iff ``action`` is ``REWRITE``;
        ``status`` is ``PENDING`` only for ``REQUEST_HUMAN_APPROVAL`` or
        ``ESCALATE``; the result is deterministic for a given
        (request, effective-constitution, engine-version).
    """

    api_version: ApiVersion
    id: UUID
    request_id: UUID
    action: VerdictAction
    risk: RiskAssessment
    status: ResultStatus
    decided_at: datetime
    transformed_action: Action | None = None
    warnings: tuple[str, ...] = ()
    determining_rule_id: str | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)
