"""The root input aggregate: :class:`DecisionRequest`.

See ``docs/decision-model.md`` §2.1. The ``DecisionRequest`` is the unit of
evaluation, of idempotency, and of audit. It is the concrete realisation of what
``docs/architecture.md`` and ``docs/constitution-engine.md`` informally called a
"Proposal".
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .action import Action
from .aliases import ApiVersion
from .context import DecisionContext
from .principals import Actor, Resource, Target


@dataclass(slots=True, frozen=True)
class DecisionRequest:
    """A complete, self-contained description of one action awaiting a verdict.

    Required
        ``api_version``: the Decision Model schema version (e.g. ``nce/v1``).
        (Wire spelling is ``apiVersion``; the snake_case mapping is a
        serialisation concern, deferred.)
        ``id``: unique request identifier (UUIDv7 by convention).
        ``actor``: who proposes the action.
        ``action``: what is proposed.
        ``context``: where/when/under what policy (embeds the environment).
        ``submitted_at``: client-asserted submission time.

    Optional
        ``target``: the affected party.
        ``resource``: the asset/data acted upon.
        ``idempotency_key``: opaque key enabling safe retries
        (``docs/decision-model.md`` §9).
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Composes one :class:`~core.domain.principals.Actor`, one
        :class:`~core.domain.action.Action`, and one
        :class:`~core.domain.context.DecisionContext`; composes zero-or-one
        :class:`~core.domain.principals.Target` and zero-or-one
        :class:`~core.domain.principals.Resource`. Referenced by exactly one
        :class:`~core.domain.result.EvaluationResult` and exactly one
        :class:`~core.domain.audit.AuditRecord`.

    Invariants (documented, not enforced here)
        ``id`` is unique and immutable; at least one of ``target`` or ``resource``
        is present (an action with neither subject nor object is not evaluable);
        the request is immutable once accepted — corrections are new requests.
    """

    api_version: ApiVersion
    id: UUID
    actor: Actor
    action: Action
    context: DecisionContext
    submitted_at: datetime
    target: Target | None = None
    resource: Resource | None = None
    idempotency_key: str | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)
