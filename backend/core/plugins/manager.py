"""Plugin Manager for coordinating plugin lifecycle and registries."""

from typing import Any

from .exceptions import PluginDependencyError, PluginLifecycleError, PluginRegistrationError
from .metadata import Capability
from .plugin import Plugin
from .registry import CapabilityRegistry


class PluginManager:
    """Manages plugin discovery, lifecycle, and capability dispatching.
    
    The manager owns the individual capability registries and guarantees
    that plugins are initialized in topological order based on dependencies.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        # Isolated registries per capability
        self._registries: dict[Capability, CapabilityRegistry[Any]] = {
            cap: CapabilityRegistry() for cap in Capability
        }
        self._initialized: list[str] = []

    def get_registry(self, capability: Capability) -> CapabilityRegistry[Any]:
        """Return the isolated registry for a given capability."""
        return self._registries[capability]

    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin with the manager."""
        metadata = plugin.metadata
        if metadata.id in self._plugins:
            raise PluginRegistrationError(f"Plugin with ID {metadata.id} is already registered.")
        
        try:
            plugin.load()
        except Exception as e:
            raise PluginLifecycleError(f"Failed to load plugin {metadata.id}: {e}") from e

        self._plugins[metadata.id] = plugin

    def _topological_sort(self) -> list[str]:
        """Resolve dependencies and return an ordered list of plugin IDs."""
        visited: set[str] = set()
        temp_mark: set[str] = set()
        order: list[str] = []

        def visit(plugin_id: str) -> None:
            if plugin_id in temp_mark:
                raise PluginDependencyError(f"Cyclic dependency detected involving plugin {plugin_id}")
            if plugin_id not in visited:
                if plugin_id not in self._plugins:
                    raise PluginDependencyError(f"Missing dependency: {plugin_id}")
                
                temp_mark.add(plugin_id)
                plugin = self._plugins[plugin_id]
                for dep in plugin.metadata.dependencies:
                    visit(dep)
                
                temp_mark.remove(plugin_id)
                visited.add(plugin_id)
                order.append(plugin_id)

        for pid in self._plugins:
            if pid not in visited:
                visit(pid)
                
        return order

    def resolve_and_initialize(self) -> None:
        """Resolve dependencies and initialize all loaded plugins."""
        order = self._topological_sort()
        
        for plugin_id in order:
            if plugin_id in self._initialized:
                continue
                
            plugin = self._plugins[plugin_id]
            try:
                plugin.initialize()
            except Exception as e:
                raise PluginLifecycleError(f"Failed to initialize plugin {plugin_id}: {e}") from e
                
            # Dispatch capabilities to respective registries
            for cap in plugin.metadata.capabilities:
                try:
                    provider = plugin.get_capability_provider(cap)
                    self._registries[cap].register(plugin_id, provider)
                except Exception as e:
                    raise PluginRegistrationError(f"Failed to register capability {cap} for plugin {plugin_id}: {e}") from e
            
            self._initialized.append(plugin_id)

    def shutdown_all(self) -> None:
        """Shutdown and unload all initialized plugins in reverse order."""
        for plugin_id in reversed(self._initialized):
            plugin = self._plugins[plugin_id]
            try:
                plugin.shutdown()
                plugin.unload()
            except Exception as e:
                raise PluginLifecycleError(f"Failed to shutdown/unload plugin {plugin_id}: {e}") from e
            
            for cap in plugin.metadata.capabilities:
                self._registries[cap].unregister(plugin_id)
                
        self._initialized.clear()
        self._plugins.clear()
