"""Unit tests for the Plugin System."""

import unittest
from typing import Any

from backend.core.plugins.exceptions import PluginDependencyError, PluginLifecycleError, PluginRegistrationError
from backend.core.plugins.manager import PluginManager
from backend.core.plugins.metadata import Capability, PluginMetadata
from backend.core.plugins.plugin import Plugin


class DummyPlugin(Plugin):
    def __init__(self, metadata: PluginMetadata, raise_on_load: bool = False, raise_on_init: bool = False):
        self._metadata = metadata
        self.raise_on_load = raise_on_load
        self.raise_on_init = raise_on_init
        self.loaded = False
        self.initialized = False
        self.shutdown_called = False
        self.unloaded = False

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def load(self) -> None:
        if self.raise_on_load:
            raise RuntimeError("load error")
        self.loaded = True

    def initialize(self) -> None:
        if self.raise_on_init:
            raise RuntimeError("init error")
        self.initialized = True

    def shutdown(self) -> None:
        self.shutdown_called = True

    def unload(self) -> None:
        self.unloaded = True

    def get_capability_provider(self, capability: Capability) -> Any:
        return f"provider_for_{capability.name}"


class TestPluginSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = PluginManager()

    def test_successful_registration_and_lifecycle(self) -> None:
        meta = PluginMetadata(id="test.plugin", version="1.0", author="test", capabilities=(Capability.MATCHER,))
        plugin = DummyPlugin(meta)

        self.manager.register_plugin(plugin)
        self.assertTrue(plugin.loaded)
        self.assertFalse(plugin.initialized)

        self.manager.resolve_and_initialize()
        self.assertTrue(plugin.initialized)

        # Verify capability routing
        registry = self.manager.get_registry(Capability.MATCHER)
        self.assertEqual(registry.get("test.plugin"), "provider_for_MATCHER")

        self.manager.shutdown_all()
        self.assertTrue(plugin.shutdown_called)
        self.assertTrue(plugin.unloaded)

        # Verify unregistration
        with self.assertRaises(PluginRegistrationError):
            registry.get("test.plugin")

    def test_dependency_resolution_order(self) -> None:
        meta_a = PluginMetadata(
            id="plugin.a", version="1.0", author="test", capabilities=(), dependencies=("plugin.b",)
        )
        meta_b = PluginMetadata(id="plugin.b", version="1.0", author="test", capabilities=())

        plugin_a = DummyPlugin(meta_a)
        plugin_b = DummyPlugin(meta_b)

        # Register out of order
        self.manager.register_plugin(plugin_a)
        self.manager.register_plugin(plugin_b)

        # Test private topological sort explicitly for test verification
        order = self.manager._topological_sort()
        self.assertEqual(order, ["plugin.b", "plugin.a"])

        self.manager.resolve_and_initialize()
        self.assertTrue(plugin_b.initialized)
        self.assertTrue(plugin_a.initialized)

    def test_cyclic_dependencies(self) -> None:
        meta_a = PluginMetadata(
            id="plugin.a", version="1.0", author="test", capabilities=(), dependencies=("plugin.b",)
        )
        meta_b = PluginMetadata(
            id="plugin.b", version="1.0", author="test", capabilities=(), dependencies=("plugin.a",)
        )

        self.manager.register_plugin(DummyPlugin(meta_a))
        self.manager.register_plugin(DummyPlugin(meta_b))

        with self.assertRaises(PluginDependencyError):
            self.manager.resolve_and_initialize()

    def test_missing_dependencies(self) -> None:
        meta_a = PluginMetadata(id="plugin.a", version="1.0", author="test", capabilities=(), dependencies=("missing",))
        self.manager.register_plugin(DummyPlugin(meta_a))

        with self.assertRaises(PluginDependencyError):
            self.manager.resolve_and_initialize()

    def test_plugin_load_failure(self) -> None:
        meta = PluginMetadata(id="test", version="1", author="test", capabilities=())
        plugin = DummyPlugin(meta, raise_on_load=True)

        with self.assertRaises(PluginLifecycleError):
            self.manager.register_plugin(plugin)

    def test_plugin_init_failure(self) -> None:
        meta = PluginMetadata(id="test", version="1", author="test", capabilities=())
        plugin = DummyPlugin(meta, raise_on_init=True)

        self.manager.register_plugin(plugin)
        with self.assertRaises(PluginLifecycleError):
            self.manager.resolve_and_initialize()

    def test_duplicate_registration(self) -> None:
        meta = PluginMetadata(id="test", version="1", author="test", capabilities=())
        self.manager.register_plugin(DummyPlugin(meta))

        with self.assertRaises(PluginRegistrationError):
            self.manager.register_plugin(DummyPlugin(meta))


if __name__ == "__main__":
    unittest.main()
