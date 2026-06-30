from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.repositories.audit_repository import AuditRepository
from backend.models.models import AuditRecordModel, ExecutionPlanRecordModel


class AuditService:
    """Service for querying audits and execution plans."""

    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def get_audits(self, organization_id: str, limit: int = 100) -> list[AuditRecordModel]:
        return await self.repo.get_audits_for_org(organization_id, limit)

    async def get_plans(self, organization_id: str, limit: int = 50) -> list[ExecutionPlanRecordModel]:
        return await self.repo.get_plans_for_org(organization_id, limit)
