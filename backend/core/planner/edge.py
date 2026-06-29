"""A directed edge in an execution plan graph."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(slots=True, frozen=True)
class PlanEdge:
    """A directed dependency between two PlanNodes.

    Required
        ``source_id``: the node that must complete first.
        ``target_id``: the node that depends on the source.

    Optional
        ``condition``: runtime criteria for traversal (e.g., "on_success", "on_failure").
        ``extensions``: uninterpreted edge properties (e.g., data mapping config).
    """

    source_id: str
    target_id: str
    condition: str | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)
