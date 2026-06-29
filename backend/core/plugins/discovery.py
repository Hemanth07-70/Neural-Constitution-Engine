"""Discovery mechanisms for finding plugins."""

import importlib.metadata
import inspect
from types import ModuleType

from .exceptions import PluginDiscoveryError
from .plugin import Plugin


class PluginDiscoverer:
    """Discovers plugins in memory without performing raw filesystem traversal.
    
    Supports discovery via explicit module references or Python entry points.
    """

    @staticmethod
    def discover_from_modules(modules: list[ModuleType]) -> list[Plugin]:
        """Scan a list of loaded modules for Plugin subclasses and instantiate them."""
        plugins = []
        for mod in modules:
            for _, obj in inspect.getmembers(mod, inspect.isclass):
                if issubclass(obj, Plugin) and obj is not Plugin:
                    try:
                        # Attempt to instantiate the plugin without arguments
                        plugins.append(obj())
                    except Exception as e:
                        raise PluginDiscoveryError(f"Failed to instantiate plugin class {obj.__name__}: {e}") from e
        return plugins

    @staticmethod
    def discover_from_entry_points(group: str = "nce.plugins") -> list[Plugin]:
        """Discover plugins using standard Python entry points.
        
        Args:
            group: The entry point group name.
        """
        plugins = []
        try:
            entry_points = importlib.metadata.entry_points(group=group)
        except TypeError:
            # Fallback for older python versions if needed, though we require 3.12
            entry_points = importlib.metadata.entry_points().get(group, [])
            
        for ep in entry_points:
            try:
                plugin_cls = ep.load()
                if issubclass(plugin_cls, Plugin):
                    plugins.append(plugin_cls())
                else:
                    raise PluginDiscoveryError(f"Entry point {ep.name} is not a Plugin subclass.")
            except Exception as e:
                raise PluginDiscoveryError(f"Failed to load entry point {ep.name}: {e}") from e
                
        return plugins
