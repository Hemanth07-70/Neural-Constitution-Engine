"""Unit tests for the public Engine SDK."""

import tempfile
import unittest
import uuid
from datetime import UTC, datetime
from pathlib import Path

from backend.core.domain.enums import ActorType
from backend.sdk import (
    Action,
    Actor,
    ConfigurationError,
    ConstitutionValidationError,
    DecisionContext,
    DecisionRequest,
    Engine,
    EngineBuilder,
    Environment,
    EnvironmentName,
    ExecutionPlan,
    PlanMetadata,
    PlanNode,
)


class TestEngineSDK(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

        self.const_path = self.base_path / "constitution.yaml"
        self.const_path.write_text(
            "apiVersion: nce/v1\n"
            "kind: Constitution\n"
            "metadata:\n"
            "  id: test\n"
            "  version: 1.0.0\n"
            "  status: published\n"
            "  author: test\n"
            "  scope: global\n"
            "resolution:\n"
            "  strategy: most-restrictive-wins\n"
            "  default_verdict: block\n"
            "principles: []\n"
            "rules: []\n"
        )

        self.req = DecisionRequest(
            api_version="nce/v1",
            id=uuid.uuid4(),
            actor=Actor(id="test", type=ActorType.HUMAN),
            action=Action(type="test.action"),
            context=DecisionContext(
                constitution_id="test",
                constitution_version="1.0.0",
                correlation_id=uuid.uuid4(),
                environment=Environment(name=EnvironmentName.TEST, timestamp=datetime.now(UTC)),
            ),
            submitted_at=datetime.now(UTC),
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_engine_version(self) -> None:
        self.assertIsInstance(Engine.version(), str)

    def test_validate_constitution(self) -> None:
        self.assertTrue(Engine.validate_constitution(self.const_path))

        with self.assertRaises(ConstitutionValidationError):
            Engine.validate_constitution(self.base_path / "does_not_exist.yaml")

    def test_engine_load(self) -> None:
        engine = Engine.load(self.const_path)
        self.assertIsInstance(engine, Engine)

    def test_engine_evaluate(self) -> None:
        engine = Engine.load(self.const_path)
        audit = engine.evaluate(self.req)

        self.assertEqual(audit.result.action.name, "BLOCK")
        self.assertEqual(audit.explanation.determining_rule.id, "SYS-FALLBACK")

    def test_engine_evaluate_plan(self) -> None:
        engine = Engine.load(self.const_path)

        meta = PlanMetadata(id="plan-1", creator="test", created_at=datetime.now(UTC), goal_description="Test plan")
        node = PlanNode(id="A", request=self.req)
        plan = ExecutionPlan(metadata=meta, nodes=(node,), edges=())

        result = engine.evaluate_plan(plan)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.topological_order), 1)

    def test_builder_fail_configuration(self) -> None:
        builder = EngineBuilder()
        with self.assertRaises(ConfigurationError):
            builder.build("missing_file.yaml")


if __name__ == "__main__":
    unittest.main()
