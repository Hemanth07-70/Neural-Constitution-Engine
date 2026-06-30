"""Unit tests for Rule Engine interface contracts."""

import unittest
from typing import Any

from backend.core.rules.evaluator import RuleEvaluator
from backend.core.rules.matcher import RuleMatcher
from backend.core.rules.registry import RuleRegistry
from backend.core.rules.resolver import RuleResolver


class TestRuleEngineInterfaces(unittest.TestCase):
    def test_abc_instantiation_fails(self) -> None:
        """Verify that abstract base classes cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            RuleEvaluator()  # type: ignore

        with self.assertRaises(TypeError):
            RuleMatcher()  # type: ignore

        with self.assertRaises(TypeError):
            RuleResolver()  # type: ignore

        with self.assertRaises(TypeError):
            RuleRegistry()  # type: ignore

    def test_concrete_implementation(self) -> None:
        """Verify that a class implementing the ABC can be instantiated."""

        class ConcreteEvaluator(RuleEvaluator):
            def evaluate(self, request: Any, params: Any) -> Any:
                return True, {"note": "test"}

        evaluator = ConcreteEvaluator()
        self.assertTrue(isinstance(evaluator, RuleEvaluator))


if __name__ == "__main__":
    unittest.main()
