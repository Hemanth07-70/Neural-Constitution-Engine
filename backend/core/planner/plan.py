"""The Execution Plan domain model."""

from dataclasses import dataclass

from .edge import PlanEdge
from .metadata import PlanMetadata
from .node import PlanNode


@dataclass(slots=True, frozen=True)
class ExecutionPlan:
    """A directed acyclic graph (DAG) of proposed actions to be governed.

    Required
        ``metadata``: structural info about the plan.
        ``nodes``: the discrete execution steps.
        ``edges``: dependencies between nodes.
    """

    metadata: PlanMetadata
    nodes: tuple[PlanNode, ...]
    edges: tuple[PlanEdge, ...]
