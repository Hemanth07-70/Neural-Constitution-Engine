"""Utility for traversing and analyzing an ExecutionPlan graph."""

from typing import Mapping

from .edge import PlanEdge
from .exceptions import CycleDetectedError, PlanGraphError
from .node import PlanNode
from .plan import ExecutionPlan


class PlanGraph:
    """Wrapper around ExecutionPlan for topological operations."""

    def __init__(self, plan: ExecutionPlan) -> None:
        self.plan = plan
        self.node_map: Mapping[str, PlanNode] = {node.id: node for node in plan.nodes}
        
        # Build adjacency lists
        self.adj: dict[str, list[PlanEdge]] = {node.id: [] for node in plan.nodes}
        self.in_degree: dict[str, int] = {node.id: 0 for node in plan.nodes}

        for edge in plan.edges:
            if edge.source_id not in self.node_map:
                raise PlanGraphError(f"Edge references unknown source node: {edge.source_id}")
            if edge.target_id not in self.node_map:
                raise PlanGraphError(f"Edge references unknown target node: {edge.target_id}")
            
            self.adj[edge.source_id].append(edge)
            self.in_degree[edge.target_id] += 1

    def topological_sort(self) -> tuple[PlanNode, ...]:
        """Perform Kahn's Algorithm to sort nodes topologically and detect cycles.
        
        Returns:
            A tuple of PlanNode in a valid execution order.
            
        Raises:
            CycleDetectedError: If the graph is not a DAG.
        """
        queue = [node_id for node_id, degree in self.in_degree.items() if degree == 0]
        in_degree = dict(self.in_degree)
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(self.node_map[curr])

            for edge in self.adj[curr]:
                neighbor = edge.target_id
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.plan.nodes):
            # Graph has a cycle, isolate nodes with non-zero in-degree
            cyclic_nodes = [n for n, deg in in_degree.items() if deg > 0]
            raise CycleDetectedError(f"Cycle detected involving nodes: {cyclic_nodes}")

        return tuple(order)
