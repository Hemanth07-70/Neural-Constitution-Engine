"""Builder for configuring and instantiating the Engine."""

from pathlib import Path

from backend.core.constitution.loader import ConstitutionLoader
from backend.core.evaluator.pipeline import EvaluationPipeline
from backend.core.plugins.manager import PluginManager

from .config import EngineConfig
from .engine import Engine
from .exceptions import ConfigurationError


class EngineBuilder:
    """Fluent builder for the Engine."""

    def __init__(self) -> None:
        self._config = EngineConfig()

    def with_config(self, config: EngineConfig) -> "EngineBuilder":
        """Set the engine configuration."""
        self._config = config
        return self

    def build(self, constitution_path: str | Path) -> Engine:
        """Construct the Engine.

        Args:
            constitution_path: Path to the constitution file.

        Returns:
            A fully initialized Engine instance.

        Raises:
            ConfigurationError: If the internal components fail to initialize.
        """
        try:
            # 1. Load Constitution
            constitution = ConstitutionLoader().load_file(constitution_path)

            # 2. Initialize Plugins
            plugin_manager = PluginManager()
            for _path in self._config.plugin_dirs:
                # Add actual discovery mechanism if needed, otherwise this is a stub for SDK configuration
                pass

            plugin_manager.resolve_and_initialize()

            # 3. Create Pipeline
            pipeline = EvaluationPipeline()

            # 4. Construct Engine
            return Engine(
                config=self._config, constitution=constitution, plugin_manager=plugin_manager, pipeline=pipeline
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to build engine: {e}") from e
