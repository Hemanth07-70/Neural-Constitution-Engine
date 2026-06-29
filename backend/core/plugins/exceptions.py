"""Exceptions for the plugin system."""

class PluginError(Exception):
    """Base class for all plugin-related errors."""
    
class PluginRegistrationError(PluginError):
    """Raised when registering a plugin fails (e.g., duplicate id, missing capability)."""
    
class PluginDependencyError(PluginError):
    """Raised when a plugin's dependencies cannot be resolved (e.g., missing or cyclical)."""
    
class PluginLifecycleError(PluginError):
    """Raised when a plugin fails to load, initialize, shutdown, or unload."""
    
class PluginDiscoveryError(PluginError):
    """Raised when discovery fails."""
