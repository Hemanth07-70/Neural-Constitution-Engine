from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.repositories.constitution_repository import ConstitutionRepository
from backend.application.services.engine_manager import EngineManager
from backend.models.models import ConstitutionRecord
from backend.sdk.engine import Engine


class ConstitutionService:
    """Manages the Constitution lifecycle and versions."""

    def __init__(self, db: AsyncSession, engine_manager: EngineManager):
        self.db = db
        self.repo = ConstitutionRepository(db)
        self.engine_manager = engine_manager

    async def get_active_constitution(self, organization_id: str) -> ConstitutionRecord | None:
        return await self.repo.get_active_constitution(organization_id)

    async def publish(
        self, organization_id: str, author_id: str, yaml_content: str, version: str
    ) -> ConstitutionRecord:
        """Publishes a new constitution, makes it active, and invalidates the cache."""

        # 1. Validate structure using the Engine
        # We write it to a temp file or validate dict directly.
        # Since Engine.validate_constitution takes a path, we can write a temporary file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w") as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            Engine.validate_constitution(temp_path)
        finally:
            os.remove(temp_path)

        # 2. Deactivate currently active
        active = await self.repo.get_active_constitution(organization_id)
        if active:
            active.active = False
            await self.repo.save(active)

        # 3. Create new record
        record = ConstitutionRecord(
            version=version,
            author_id=author_id,
            organization_id=organization_id,
            yaml_content=yaml_content,
            active=True,
        )

        await self.repo.save(record)
        await self.db.commit()

        # 4. Invalidate engine cache so the next request loads the new active constitution
        self.engine_manager.invalidate(organization_id)

        return record

    async def rollback(self, organization_id: str, version: str) -> ConstitutionRecord:
        """Rolls back to a specific version by deactivating current and activating the target."""
        # This assumes we have a get_by_version which we didn't add yet, but this is the idea.
        raise NotImplementedError("Rollback is not fully implemented.")
