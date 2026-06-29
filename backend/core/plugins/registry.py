"""Isolated registries for plugin capabilities."""

from typing import Generic, TypeVar

from .exceptions import PluginRegistrationError

T = TypeVar("T")


class CapabilityRegistry(Generic[T]):
    """An isolated registry for a specific capability type.
    
    Registries have no knowledge of each other or the broader PluginManager.
    They simply map a plugin ID to a provider implementation.
    """

    def __init__(self) -> None:
        self._providers: dict[str, T] = {}

    def register(self, plugin_id: str, provider: T) -> None:
        """Register a provider implementation under a plugin ID."""
        if plugin_id in self._providers:
            raise PluginRegistrationError(f"Plugin {plugin_id} is already registered in this capability registry.")
        self._providers[plugin_id] = provider

    def get(self, plugin_id: str) -> T:
        """Retrieve a provider implementation by plugin ID."""
        if plugin_id not in self._providers:
            raise PluginRegistrationError(f"Plugin {plugin_id} not found in this registry.")
        return self._providers[plugin_id]

    def list_providers(self) -> list[T]:
        """Return all registered providers in this registry."""
        return list(self._providers.values())
        
    def list_keys(self) -> list[str]:
        """Return all registered plugin IDs."""
        return list(self._providers.keys())

    def unregister(self, plugin_id: str) -> None:
        """Remove a provider from the registry."""
        self._providers.pop(plugin_id, None)
