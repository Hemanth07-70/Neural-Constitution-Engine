"""Tests for the execution plan validator."""

import unittest
import uuid
from datetime import datetime, timezone

from backend.core.domain.action import Action
from backend.core.domain.context import DecisionContext, Environment
from backend.core.domain.enums import EnvironmentName
from backend.core.domain.principals import Actor
from backend.core.domain.request import DecisionRequest
from backend.core.planner.edge import PlanEdge
from backend.core.planner.metadata import PlanMetadata
from backend.core.planner.node import PlanNode
from backend.core.planner.plan import ExecutionPlan
from backend.core.planner.validator import PlanValidator


class TestPlanValidator(unittest.TestCase):
    def setUp(self):
        self.req = DecisionRequest(
            api_version="nce/v1",
            id=uuid.uuid4(),
            actor=Actor(id="test", type="agent"),
            action=Action(type="test.action", params={}),
            submitted_at=datetime.now(timezone.utc),
            context=DecisionContext(
                constitution_id="test",
                constitution_version="1.0.0",
                correlation_id=uuid.uuid4(),
                environment=Environment(name=EnvironmentName.TEST, timestamp=datetime.now(timezone.utc))
            )
        )
        self.meta = PlanMetadata(
            id="plan-1",
            creator="agent",
            created_at=datetime.now(timezone.utc),
            goal_description="Test plan"
        )
        self.node_a = PlanNode(id="A", request=self.req)
        self.node_b = PlanNode(id="B", request=self.req)

    def test_valid_plan(self):
        plan = ExecutionPlan(
            metadata=self.meta,
            nodes=(self.node_a, self.node_b),
            edges=(PlanEdge(source_id="A", target_id="B"),)
        )
        result = PlanValidator.validate(plan)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
        self.assertEqual(len(result.topological_order), 2)

    def test_invalid_plan_cycle(self):
        plan = ExecutionPlan(
            metadata=self.meta,
            nodes=(self.node_a, self.node_b),
            edges=(
                PlanEdge(source_id="A", target_id="B"),
                PlanEdge(source_id="B", target_id="A")
            )
        )
        result = PlanValidator.validate(plan)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("Cycle detected", result.errors[0])
        self.assertEqual(len(result.topological_order), 0)

    def test_warning_disconnected_node(self):
        node_c = PlanNode(id="C", request=self.req)
        plan = ExecutionPlan(
            metadata=self.meta,
            nodes=(self.node_a, self.node_b, node_c),
            edges=(PlanEdge(source_id="A", target_id="B"),)
        )
        result = PlanValidator.validate(plan)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("disconnected", result.warnings[0])
        self.assertEqual(len(result.topological_order), 3)


if __name__ == "__main__":
    unittest.main()
