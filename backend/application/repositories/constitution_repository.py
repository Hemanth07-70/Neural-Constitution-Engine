from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.models import ConstitutionRecord


class ConstitutionRepository:
    """Repository for managing Constitution versions and records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, constitution: ConstitutionRecord) -> ConstitutionRecord:
        self.session.add(constitution)
        await self.session.flush()
        return constitution

    async def get_active_constitution(self, org_id: str) -> ConstitutionRecord | None:
        stmt = (
            select(ConstitutionRecord)
            .where(ConstitutionRecord.organization_id == org_id, ConstitutionRecord.active)
            .order_by(desc(ConstitutionRecord.created_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_history(self, org_id: str) -> list[ConstitutionRecord]:
        stmt = (
            select(ConstitutionRecord)
            .where(ConstitutionRecord.organization_id == org_id)
            .order_by(desc(ConstitutionRecord.created_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
