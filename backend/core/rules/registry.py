"""Registry interface for plugins and transforms."""

from abc import ABC, abstractmethod

from .evaluator import RuleEvaluator


class RuleRegistry(ABC):
    """Registry interface for resolving named plugins and transforms.

    The registry acts as the single source of truth for third-party extensions.
    It decouples the core matching logic from the implementation details of
    custom condition evaluators.
    """

    @abstractmethod
    def register_evaluator(self, name: str, evaluator: RuleEvaluator) -> None:
        """Register a custom condition evaluator by name.

        Args:
            name: The unique identifier for the evaluator.
            evaluator: The RuleEvaluator instance.
        """
        pass

    @abstractmethod
    def get_evaluator(self, name: str) -> RuleEvaluator:
        """Retrieve an evaluator by name.

        Args:
            name: The unique identifier of the evaluator.

        Returns:
            The RuleEvaluator instance.

        Raises:
            PluginNotFoundError: If no evaluator is registered under the given name.
        """
        pass
