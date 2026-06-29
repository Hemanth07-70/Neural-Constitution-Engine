"""Plugin System for the Neural Constitution Engine."""

from .discovery import PluginDiscoverer
from .exceptions import (
    PluginDependencyError,
    PluginDiscoveryError,
    PluginError,
    PluginLifecycleError,
    PluginRegistrationError,
)
from .manager import PluginManager
from .metadata import Capability, PluginMetadata
from .plugin import Plugin
from .registry import CapabilityRegistry

__all__ = [
    "Capability",
    "CapabilityRegistry",
    "Plugin",
    "PluginDependencyError",
    "PluginDiscoverer",
    "PluginDiscoveryError",
    "PluginError",
    "PluginLifecycleError",
    "PluginManager",
    "PluginMetadata",
    "PluginRegistrationError",
]
