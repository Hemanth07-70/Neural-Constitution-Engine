"""The proposed :class:`Action`.

See ``docs/decision-model.md`` §2.6. The ``Action`` describes the verb and
parameters the actor *proposes*; it is the primary subject of rule conditions in
a constitution. The *resolved verdict* (allow/block/...) is a separate concept,
modelled by :class:`~core.domain.enums.VerdictAction`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .aliases import ActionType


@dataclass(slots=True, frozen=True)
class Action:
    """The verb and parameters of what an actor proposes to do.

    Required
        ``type``: a dotted, namespaced verb (e.g. ``db.execute``).
        ``params``: action-specific parameters (typed per action type by a
        schema registry that lives outside the pure domain).

    Optional
        ``intent``: free-text rationale supplied by the agent. **Advisory only**
        — never trusted for authorisation; the engine governs the action, not the
        stated reason for it.
        ``estimated_cost``: structured cost estimate consumed by cost rules.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Composed by exactly one
        :class:`~core.domain.request.DecisionRequest`. A ``rewrite`` verdict may
        produce a derived ``Action`` recorded as
        :attr:`~core.domain.result.EvaluationResult.transformed_action`.

    Invariants (documented, not enforced here)
        ``type`` is a non-empty namespaced verb; ``params`` conforms to the schema
        registered for ``type``.
    """

    type: ActionType
    params: Mapping[str, object] = field(default_factory=dict)
    intent: str | None = None
    estimated_cost: Mapping[str, object] | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)
