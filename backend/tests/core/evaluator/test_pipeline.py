"""Unit tests for the Deterministic Evaluation Pipeline."""

import unittest
import uuid
from types import MappingProxyType
from typing import Any

from backend.core.constitution.constitution import Constitution
from backend.core.constitution.metadata import Metadata, Resolution
from backend.core.constitution.rule import Rule, RuleAction
from backend.core.domain.action import Action
from backend.core.domain.context import DecisionContext, Environment
from backend.core.domain.enums import ActorType, EnvironmentName, RiskLevel, VerdictAction
from backend.core.domain.principals import Actor
from backend.core.domain.request import DecisionRequest
from backend.core.evaluator.exceptions import FailClosedError
from backend.core.evaluator.pipeline import EvaluationPipeline
from backend.core.evaluator.stages import PipelineStage


class TestEvaluationPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = EvaluationPipeline()
        self.request = DecisionRequest(
            api_version="nce/v1",
            id=uuid.uuid4(),
            actor=Actor(id="test", type=ActorType.HUMAN),
            action=Action(type="transfer", params={"target": "bank"}),
            submitted_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            context=DecisionContext(
                constitution_id="test",
                constitution_version="1.0",
                environment=Environment(
                    name=EnvironmentName.TEST,
                    timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                ),
                correlation_id=uuid.uuid4(),
            ),
        )
        self.base_metadata = Metadata(
            id="test-constitution", version="1.0", status="published", author="test", scope="global"
        )
        self.base_resolution = Resolution(strategy="most-restrictive-wins", default_verdict="block")

    def test_no_matching_rules_fail_closed(self) -> None:
        """Verify fallback to resolution default_verdict when no rules match."""
        constitution = Constitution(
            api_version="nce/v1",
            kind="Constitution",
            metadata=self.base_metadata,
            resolution=self.base_resolution,
            principles=(),
            rules=(),
        )

        result, explanation, audit = self.pipeline.evaluate(self.request, constitution)

        self.assertEqual(result.action, VerdictAction.BLOCK)
        self.assertEqual(result.risk.level, RiskLevel.INFORMATIONAL)
        self.assertEqual(explanation.determining_rule.id, "SYS-FALLBACK")
        self.assertEqual(audit.result.action, VerdictAction.BLOCK)

    def test_one_matching_rule(self) -> None:
        """Verify a single matched rule dictates the verdict."""
        rule = Rule(
            id="R001",
            condition=MappingProxyType({"field": "action.type", "op": "equals", "value": "transfer"}),
            action=RuleAction(type="allow", message="Allowed transfer"),
            severity="low",
        )
        constitution = Constitution(
            api_version="nce/v1",
            kind="Constitution",
            metadata=self.base_metadata,
            resolution=self.base_resolution,
            principles=(),
            rules=(rule,),
        )

        result, explanation, audit = self.pipeline.evaluate(self.request, constitution)

        self.assertEqual(result.action, VerdictAction.ALLOW)
        self.assertEqual(result.risk.level, RiskLevel.LOW)
        self.assertEqual(explanation.determining_rule.id, "R001")

    def test_multiple_matching_rules_aggregate_risk(self) -> None:
        """Verify risk aggregates to highest severity among all matches."""
        r1 = Rule(
            id="R001",
            condition=MappingProxyType({"field": "action.type", "op": "equals", "value": "transfer"}),
            action=RuleAction(type="allow"),
            severity="low",
        )
        r2 = Rule(
            id="R002",
            condition=MappingProxyType({"field": "action.type", "op": "equals", "value": "transfer"}),
            action=RuleAction(type="warn"),
            severity="medium",
        )
        constitution = Constitution(
            api_version="nce/v1",
            kind="Constitution",
            metadata=self.base_metadata,
            resolution=self.base_resolution,
            principles=(),
            rules=(r1, r2),
        )

        result, explanation, audit = self.pipeline.evaluate(self.request, constitution)

        self.assertEqual(result.risk.level, RiskLevel.MEDIUM)
        # 2 matches = 2 risk factors
        self.assertEqual(len(result.risk.factors), 2)

    def test_rule_conflicts_resolution(self) -> None:
        """Verify most-restrictive-wins resolves conflicts and notes contenders."""
        r_allow = Rule(
            id="ALLOW-1",
            condition=MappingProxyType({"field": "action.type", "op": "equals", "value": "transfer"}),
            action=RuleAction(type="allow"),
        )
        r_block = Rule(
            id="BLOCK-1",
            condition=MappingProxyType({"field": "action.type", "op": "equals", "value": "transfer"}),
            action=RuleAction(type="block"),
        )
        constitution = Constitution(
            api_version="nce/v1",
            kind="Constitution",
            metadata=self.base_metadata,
            resolution=self.base_resolution,
            principles=(),
            rules=(r_allow, r_block),
        )

        result, explanation, audit = self.pipeline.evaluate(self.request, constitution)

        self.assertEqual(result.action, VerdictAction.BLOCK)
        self.assertEqual(explanation.determining_rule.id, "BLOCK-1")
        self.assertEqual(len(explanation.resolution.overridden_contenders), 1)
        self.assertEqual(explanation.resolution.overridden_contenders[0].id, "ALLOW-1")

    def test_fail_closed_on_unhandled_exception(self) -> None:
        """Verify pipeline wraps unhandled exceptions in FailClosedError."""

        class ErrorStage(PipelineStage):
            def execute(self, req: Any, const: Any, ctx: Any, data: Any) -> Any:
                raise RuntimeError("Unexpected DB outage")

        pipeline = EvaluationPipeline(stages=[ErrorStage()])

        constitution = Constitution(
            api_version="nce/v1",
            kind="Constitution",
            metadata=self.base_metadata,
            resolution=self.base_resolution,
            principles=(),
            rules=(),
        )

        with self.assertRaises(FailClosedError) as ctx:
            pipeline.evaluate(self.request, constitution)

        self.assertIn("Unexpected DB outage", str(ctx.exception))

    def test_deterministic_replay(self) -> None:
        """Verify identical requests yield identically hashed/structured outputs."""
        r1 = Rule(
            id="R1",
            condition=MappingProxyType({"field": "action.type", "op": "equals", "value": "transfer"}),
            action=RuleAction(type="allow"),
        )
        constitution = Constitution(
            api_version="nce/v1",
            kind="Constitution",
            metadata=self.base_metadata,
            resolution=self.base_resolution,
            principles=(),
            rules=(r1,),
        )

        # We test that no random mutations occur
        res1, expl1, audit1 = self.pipeline.evaluate(self.request, constitution)
        res2, expl2, audit2 = self.pipeline.evaluate(self.request, constitution)

        self.assertEqual(res1.action, res2.action)
        self.assertEqual(expl1.determining_rule.id, expl2.determining_rule.id)
        # Content hashes should be identical (though currently mocked)
        self.assertEqual(audit1.content_hash, audit2.content_hash)


if __name__ == "__main__":
    unittest.main()
