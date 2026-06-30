"""Semantic and structural validation of Execution Plans."""

from dataclasses import dataclass, field
from typing import Any

from .exceptions import CycleDetectedError, PlanGraphError
from .graph import PlanGraph
from .node import PlanNode
from .plan import ExecutionPlan


@dataclass(slots=True, frozen=True)
class PlanValidationResult:
    """The outcome of verifying a plan's structural integrity.

    Required
        ``is_valid``: True if the plan is structurally sound and acyclic.

    Optional
        ``errors``: fatal structural errors (e.g. cycles, missing nodes).
        ``warnings``: non-fatal issues (e.g. disconnected nodes).
        ``topological_order``: a valid execution sequence if is_valid is True.
    """

    is_valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    topological_order: tuple[PlanNode, ...] = field(default_factory=tuple)
    failed_node_id: str | None = None
    node_results: dict[str, Any] = field(default_factory=dict)


class PlanValidator:
    """Validates an ExecutionPlan without evaluating rules or running logic."""

    @staticmethod
    def validate(plan: ExecutionPlan) -> PlanValidationResult:
        """Verify the structural integrity of a plan."""
        errors = []
        warnings = []
        order = []

        # 1. Structural constraints
        if not plan.nodes:
            warnings.append("Plan contains no nodes.")

        # 2. Graph topology
        try:
            graph = PlanGraph(plan)

            # Check for disconnected components (warnings only)
            # A node with no in-edges and no out-edges is disconnected unless it's the only node
            if len(plan.nodes) > 1:
                for node in plan.nodes:
                    if graph.in_degree[node.id] == 0 and not graph.adj[node.id]:
                        warnings.append(f"Node {node.id} is disconnected from the graph.")

            # Attempt topological sort (validates DAG)
            order = list(graph.topological_sort())

        except CycleDetectedError as e:
            errors.append(str(e))
        except PlanGraphError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"Unexpected validation error: {e}")

        return PlanValidationResult(
            is_valid=len(errors) == 0, errors=tuple(errors), warnings=tuple(warnings), topological_order=tuple(order)
        )
