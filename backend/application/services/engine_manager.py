import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.cache.engine_cache import EngineCache
from backend.application.repositories.constitution_repository import ConstitutionRepository
from backend.core.constitution.loader import ConstitutionLoader
from backend.core.evaluator.pipeline import EvaluationPipeline
from backend.core.plugins.manager import PluginManager
from backend.sdk.config import EngineConfig
from backend.sdk.engine import Engine


class EngineManager:
    """Manages the lifecycle, caching, and instantiation of SDK Engine instances."""

    def __init__(self, cache: EngineCache):
        self.cache = cache

    def _build_engine_from_yaml(self, yaml_content: str) -> Engine:
        """Constructs an Engine directly from YAML string using the Core components."""
        data = yaml.safe_load(yaml_content)
        constitution = ConstitutionLoader().load_dict(data)

        config = EngineConfig()
        plugin_manager = PluginManager()
        plugin_manager.resolve_and_initialize()

        pipeline = EvaluationPipeline()

        return Engine(config=config, constitution=constitution, plugin_manager=plugin_manager, pipeline=pipeline)

    async def get_engine(
        self, db: AsyncSession, organization_id: str, constitution_version: str | None = None
    ) -> Engine:
        """
        Retrieves an Engine instance for the given organization.
        If constitution_version is not provided, it fetches the currently active version.
        """
        repo = ConstitutionRepository(db)

        if constitution_version is None:
            active_record = await repo.get_active_constitution(organization_id)
            if not active_record:
                import os

                from backend.api.config import settings

                if os.path.exists(settings.NCE_CONSTITUTION_PATH):
                    with open(settings.NCE_CONSTITUTION_PATH) as f:
                        yaml_content = f.read()
                    constitution_version = "1.0.0"
                else:
                    raise ValueError(f"No active constitution found for organization: {organization_id}")
            else:
                constitution_version = active_record.version
                yaml_content = active_record.yaml_content
        else:
            # If a specific version is requested, we would fetch that specific version.
            # For simplicity, assuming the active record is what we want or we fetch history.
            # In a full implementation, we'd add `get_by_version` to the repo.
            raise NotImplementedError("Fetching specific version engine not fully implemented yet.")

        # Check cache
        engine = self.cache.get(organization_id, constitution_version)
        if engine:
            return engine

        # Cache Miss - Build and Cache
        engine = self._build_engine_from_yaml(yaml_content)
        self.cache.set(organization_id, constitution_version, engine)

        return engine

    def invalidate(self, organization_id: str) -> None:
        """Invalidates the engine cache for an organization."""
        self.cache.invalidate(organization_id)

    async def reload_engine(self, db: AsyncSession, organization_id: str) -> Engine:
        """Forces an invalidation and eager reload of the engine for an organization."""
        self.invalidate(organization_id)
        return await self.get_engine(db, organization_id)
