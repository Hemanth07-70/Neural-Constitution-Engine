"""An individual node in an execution plan."""

from dataclasses import dataclass, field
from typing import Mapping

from backend.core.domain.request import DecisionRequest


@dataclass(slots=True, frozen=True)
class PlanNode:
    """A discrete step in an execution plan, wrapping a DecisionRequest.

    Required
        ``id``: unique identifier within the graph (e.g. "step_1").
        ``request``: the proposed action and context to be governed.

    Optional
        ``preconditions``: required state or outputs before this node executes.
        ``postconditions``: expected state or outputs after this node executes.
        ``estimated_cost``: structured cost prediction for this node.
        ``human_approval_required``: boolean flag explicitly requesting human review.
        ``extensions``: uninterpreted properties (e.g., custom risk markers).
    """

    id: str
    request: DecisionRequest
    preconditions: tuple[str, ...] = field(default_factory=tuple)
    postconditions: tuple[str, ...] = field(default_factory=tuple)
    estimated_cost: Mapping[str, object] | None = None
    human_approval_required: bool = False
    extensions: Mapping[str, object] = field(default_factory=dict)
