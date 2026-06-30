"""Tests for execution plan graph structures and topological sorting."""

import unittest
import uuid
from datetime import UTC, datetime

from backend.core.domain.action import Action
from backend.core.domain.context import DecisionContext, Environment
from backend.core.domain.enums import ActorType, EnvironmentName
from backend.core.domain.principals import Actor
from backend.core.domain.request import DecisionRequest
from backend.core.planner.edge import PlanEdge
from backend.core.planner.exceptions import CycleDetectedError, PlanGraphError
from backend.core.planner.graph import PlanGraph
from backend.core.planner.metadata import PlanMetadata
from backend.core.planner.node import PlanNode
from backend.core.planner.plan import ExecutionPlan


class TestPlanGraph(unittest.TestCase):
    def setUp(self) -> None:
        self.req = DecisionRequest(
            api_version="nce/v1",
            id=uuid.uuid4(),
            actor=Actor(id="test", type=ActorType.AGENT),
            action=Action(type="test.action", params={}),
            submitted_at=datetime.now(UTC),
            context=DecisionContext(
                constitution_id="test",
                constitution_version="1.0.0",
                correlation_id=uuid.uuid4(),
                environment=Environment(name=EnvironmentName.TEST, timestamp=datetime.now(UTC)),
            ),
        )
        self.meta = PlanMetadata(
            id="plan-1", creator="agent", created_at=datetime.now(UTC), goal_description="Test plan"
        )
        self.node_a = PlanNode(id="A", request=self.req)
        self.node_b = PlanNode(id="B", request=self.req)
        self.node_c = PlanNode(id="C", request=self.req)

    def test_topological_sort_linear(self) -> None:
        """Verify linear plan sorts correctly: A -> B -> C"""
        edges = (PlanEdge(source_id="A", target_id="B"), PlanEdge(source_id="B", target_id="C"))
        plan = ExecutionPlan(
            metadata=self.meta,
            nodes=(self.node_b, self.node_a, self.node_c),  # Scrambled
            edges=edges,
        )

        graph = PlanGraph(plan)
        order = graph.topological_sort()

        self.assertEqual(len(order), 3)
        self.assertEqual(order[0].id, "A")
        self.assertEqual(order[1].id, "B")
        self.assertEqual(order[2].id, "C")

    def test_topological_sort_fork_join(self) -> None:
        """Verify DAG sort: A -> B, A -> C, B -> D, C -> D"""
        node_d = PlanNode(id="D", request=self.req)
        edges = (
            PlanEdge(source_id="A", target_id="B"),
            PlanEdge(source_id="A", target_id="C"),
            PlanEdge(source_id="B", target_id="D"),
            PlanEdge(source_id="C", target_id="D"),
        )
        plan = ExecutionPlan(metadata=self.meta, nodes=(self.node_a, self.node_b, self.node_c, node_d), edges=edges)

        graph = PlanGraph(plan)
        order = graph.topological_sort()

        self.assertEqual(len(order), 4)
        self.assertEqual(order[0].id, "A")
        self.assertEqual(order[-1].id, "D")
        self.assertIn(order[1].id, ["B", "C"])
        self.assertIn(order[2].id, ["B", "C"])

    def test_cycle_detection(self) -> None:
        """Verify cycle A -> B -> C -> A raises CycleDetectedError"""
        edges = (
            PlanEdge(source_id="A", target_id="B"),
            PlanEdge(source_id="B", target_id="C"),
            PlanEdge(source_id="C", target_id="A"),
        )
        plan = ExecutionPlan(metadata=self.meta, nodes=(self.node_a, self.node_b, self.node_c), edges=edges)

        graph = PlanGraph(plan)
        with self.assertRaises(CycleDetectedError):
            graph.topological_sort()

    def test_invalid_edge_reference(self) -> None:
        """Verify edge referencing unknown node raises PlanGraphError"""
        edges = (PlanEdge(source_id="A", target_id="UNKNOWN"),)
        plan = ExecutionPlan(metadata=self.meta, nodes=(self.node_a,), edges=edges)

        with self.assertRaises(PlanGraphError):
            PlanGraph(plan)


if __name__ == "__main__":
    unittest.main()
