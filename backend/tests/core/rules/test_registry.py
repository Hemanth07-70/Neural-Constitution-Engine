"""Unit tests for RuleRegistry behavior."""

import unittest
from typing import Any

from backend.core.domain.request import DecisionRequest
from backend.core.rules.evaluator import RuleEvaluator
from backend.core.rules.exceptions import PluginNotFoundError
from backend.core.rules.registry import RuleRegistry


class SimpleRegistry(RuleRegistry):
    def __init__(self) -> None:
        self._evaluators: dict[str, RuleEvaluator] = {}

    def register_evaluator(self, name: str, evaluator: RuleEvaluator) -> None:
        self._evaluators[name] = evaluator

    def get_evaluator(self, name: str) -> RuleEvaluator:
        if name not in self._evaluators:
            raise PluginNotFoundError(f"Plugin {name} not found.")
        return self._evaluators[name]


class DummyEvaluator(RuleEvaluator):
    def evaluate(self, request: DecisionRequest, params: dict[str, object]) -> tuple[bool, dict[str, Any] | None]:
        return True, None


class TestRuleRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SimpleRegistry()

    def test_register_and_get(self) -> None:
        """Verify successful registration and retrieval."""
        evaluator = DummyEvaluator()
        self.registry.register_evaluator("dummy", evaluator)

        retrieved = self.registry.get_evaluator("dummy")
        self.assertIs(retrieved, evaluator)

    def test_get_not_found(self) -> None:
        """Verify PluginNotFoundError is raised on missing plugin."""
        with self.assertRaises(PluginNotFoundError):
            self.registry.get_evaluator("missing")


if __name__ == "__main__":
    unittest.main()
