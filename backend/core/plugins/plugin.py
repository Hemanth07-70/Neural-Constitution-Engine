"""Base plugin interface."""

from abc import ABC, abstractmethod
from typing import Any

from .metadata import Capability, PluginMetadata


class Plugin(ABC):
    """Abstract base class for all Constitution Engine plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return the plugin's metadata."""
        pass

    @abstractmethod
    def load(self) -> None:
        """Called when the plugin is first loaded into the manager."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Called to initialize the plugin after all dependencies are loaded."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Called to gracefully shutdown the plugin's resources."""
        pass

    @abstractmethod
    def unload(self) -> None:
        """Called just before the plugin is removed from memory."""
        pass

    @abstractmethod
    def get_capability_provider(self, capability: Capability) -> Any:
        """Return the concrete provider implementation for a given capability.

        Args:
            capability: The requested Capability enum.

        Returns:
            The implementation object (e.g., RuleEvaluator instance).
        """
        pass
