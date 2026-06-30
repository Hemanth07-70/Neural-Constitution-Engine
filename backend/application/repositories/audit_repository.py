from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.models import AuditRecordModel, ExecutionPlanRecordModel


class AuditRepository:
    """Repository for managing audit and execution plan records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_audit(self, audit_db: AuditRecordModel) -> AuditRecordModel:
        self.session.add(audit_db)
        await self.session.flush()
        return audit_db

    async def save_plan_evaluation(self, plan_db: ExecutionPlanRecordModel) -> ExecutionPlanRecordModel:
        self.session.add(plan_db)
        await self.session.flush()
        return plan_db

    async def get_audits_for_org(self, org_id: str, limit: int = 100) -> list[AuditRecordModel]:
        stmt = (
            select(AuditRecordModel)
            .where(AuditRecordModel.organization_id == org_id)
            .order_by(desc(AuditRecordModel.recorded_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_plans_for_org(self, org_id: str, limit: int = 50) -> list[ExecutionPlanRecordModel]:
        stmt = (
            select(ExecutionPlanRecordModel)
            .where(ExecutionPlanRecordModel.organization_id == org_id)
            .order_by(desc(ExecutionPlanRecordModel.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
