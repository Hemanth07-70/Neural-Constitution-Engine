"""The structured rationale: :class:`Explanation` and its value objects.

Every verdict — including ``allow`` — carries an :class:`Explanation`. See
``docs/constitution-engine.md`` §9 and ``docs/decision-model.md`` §2.10. The
explanation must be traceable (names the determining rule and its principle),
complete (lists overridden contenders and *why* they lost), and reproducible
(pins versions via :class:`~core.domain.provenance.Provenance`).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from uuid import UUID

from .aliases import Category, PluginRef
from .enums import RiskLevel, ResolutionStrategy, Scope, VerdictAction
from .provenance import Provenance


@dataclass(slots=True, frozen=True)
class Verdict:
    """The compact ``{action, risk_level}`` summary mirrored in an explanation.

    A small value object so the explanation can restate the outcome without
    embedding the full :class:`~core.domain.result.EvaluationResult`.
    """

    action: VerdictAction
    risk_level: RiskLevel


@dataclass(slots=True, frozen=True)
class DeterminingRule:
    """A snapshot of the rule that decided the verdict.

    A frozen copy of the rule's salient fields taken at decision time, so the
    explanation remains meaningful even as the underlying constitution evolves.

    Required
        ``id``, ``scope``, ``category``, ``severity``, ``principle`` (the id of
        the principle served), ``statement`` (the principle's human-readable
        intent), ``message`` (the rule's caller-facing message).

    Optional
        ``title``: a human-friendly rule title.
        ``extensions``: namespaced data preserved but not interpreted by the core.
    """

    id: str
    scope: Scope
    category: Category
    severity: RiskLevel
    principle: str
    statement: str
    message: str
    title: str | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class OverriddenContender:
    """A rule that matched but did not win conflict resolution.

    Required
        ``id``: the contending rule.
        ``scope``: its scope.
        ``action``: the verdict action it proposed.
        ``reason``: why it lost (e.g. ``lower authority``).

    Optional
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Listed by a :class:`Resolution`.
    """

    id: str
    scope: Scope
    action: VerdictAction
    reason: str
    extensions: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Resolution:
    """How the winning action was selected among matched rules.

    Required
        ``strategy``: the conflict-resolution strategy applied.
        ``decided_by``: the precedence criterion that settled it (e.g.
        ``action-authority``; see ``docs/constitution-engine.md`` §6).

    Optional
        ``overridden_contenders``: rules that matched but did not win.
        ``extensions``: namespaced data preserved but not interpreted by the core.
    """

    strategy: ResolutionStrategy
    decided_by: str
    overridden_contenders: tuple[OverriddenContender, ...] = ()
    extensions: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Explanation:
    """The complete, structured rationale for a single verdict.

    Required
        ``decision_id``: links to the result/audit record.
        ``verdict``: the ``{action, risk_level}`` summary.
        ``determining_rule``: the snapshot of the rule that decided the outcome.
        ``resolution``: how that rule won over the contenders.

    Optional
        ``warnings``: advisory notes that still apply.
        ``applied_transforms``: ``name@version`` of transforms applied.
        ``references``: external policy/regulatory citations.
        ``provenance``: pinned versions for reproducibility.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Explains exactly one :class:`~core.domain.result.EvaluationResult`;
        embedded in the :class:`~core.domain.audit.AuditRecord`.

    Invariants (documented, not enforced here)
        Exists for every result; names the determining rule and why contenders
        lost; identical inputs yield identical explanations under canonical
        serialisation.
    """

    decision_id: UUID
    verdict: Verdict
    determining_rule: DeterminingRule
    resolution: Resolution
    warnings: tuple[str, ...] = ()
    applied_transforms: tuple[PluginRef, ...] = ()
    references: tuple[str, ...] = ()
    provenance: Provenance | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)
