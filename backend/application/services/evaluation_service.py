from sqlalchemy.ext.asyncio import AsyncSession

from backend.api import adapters
from backend.api.schemas.evaluate import AuditRecordSchema, DecisionRequestSchema
from backend.api.schemas.plans import ExecutionPlanSchema, PlanValidationResultSchema
from backend.application.repositories.audit_repository import AuditRepository
from backend.application.services.engine_manager import EngineManager
from backend.models.models import AuditRecordModel, ExecutionPlanRecordModel


class EvaluationService:
    """Orchestrates evaluations bridging HTTP schemas, Engine Manager, and Persistence."""

    def __init__(self, db: AsyncSession, engine_manager: EngineManager):
        self.db = db
        self.engine_manager = engine_manager
        self.audit_repo = AuditRepository(db)

    async def evaluate_decision(self, organization_id: str, request_data: DecisionRequestSchema) -> AuditRecordSchema:
        """Evaluates a single decision and persists the audit."""

        # 1. Fetch Engine
        engine = await self.engine_manager.get_engine(self.db, organization_id)

        # 2. Translate Pydantic -> SDK
        sdk_request = adapters.to_sdk_decision_request(request_data)

        # 3. Evaluate
        sdk_audit = engine.evaluate(sdk_request)

        # 4. Translate SDK -> Pydantic
        pydantic_audit = adapters.from_sdk_audit_record(sdk_audit)

        # 5. Persist to DB
        audit_db = AuditRecordModel(
            id=pydantic_audit.id,
            organization_id=organization_id,
            api_version=pydantic_audit.request.api_version,
            request_data=pydantic_audit.request.model_dump(mode="json"),
            result_data=pydantic_audit.result.model_dump(mode="json"),
            explanation_data=pydantic_audit.explanation.model_dump(mode="json"),
            recorded_at=pydantic_audit.recorded_at.replace(tzinfo=None),
        )
        await self.audit_repo.save_audit(audit_db)
        await self.db.commit()

        return pydantic_audit

    async def evaluate_plan(
        self, organization_id: str, request_data: ExecutionPlanSchema
    ) -> PlanValidationResultSchema:
        """Evaluates a plan and persists the validation result and all its component audits."""

        engine = await self.engine_manager.get_engine(self.db, organization_id)

        sdk_plan = adapters.to_sdk_execution_plan(request_data)

        # Evaluate Plan using Engine
        sdk_result = engine.evaluate_plan(sdk_plan)
        pydantic_result = adapters.from_sdk_plan_validation_result(sdk_result)

        # Persist Plan Record
        import uuid

        plan_db = ExecutionPlanRecordModel(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            plan_data=request_data.model_dump(mode="json"),
            validation_result_data=pydantic_result.model_dump(mode="json"),
        )
        await self.audit_repo.save_plan_evaluation(plan_db)

        # Save individual node audits
        if pydantic_result.node_results:
            for audit in pydantic_result.node_results.values():
                audit_db = AuditRecordModel(
                    id=audit.id,
                    organization_id=organization_id,
                    api_version=audit.request.api_version,
                    request_data=audit.request.model_dump(mode="json"),
                    result_data=audit.result.model_dump(mode="json"),
                    explanation_data=audit.explanation.model_dump(mode="json"),
                    recorded_at=audit.recorded_at.replace(tzinfo=None),
                )
                await self.audit_repo.save_audit(audit_db)

        await self.db.commit()

        return pydantic_result
