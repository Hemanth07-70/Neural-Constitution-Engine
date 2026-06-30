"""Execution plan evaluation endpoints."""

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_evaluation_service, verify_api_key_or_token
from backend.api.schemas.plans import ExecutionPlanSchema, PlanValidationResultSchema
from backend.application.services.evaluation_service import EvaluationService

router = APIRouter()


@router.post(
    "/plans/evaluate",
    response_model=PlanValidationResultSchema,
    summary="Validate an ExecutionPlan",
    description="Validates the structural integrity and topological ordering of an execution plan DAG.",
)
async def evaluate_plan(
    plan_data: ExecutionPlanSchema,
    eval_service: EvaluationService = Depends(get_evaluation_service),
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
) -> PlanValidationResultSchema:
    """Evaluate an execution plan using the Application Layer Evaluation Service."""
    organization_id = auth_context.get("organization_id")
    if not organization_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Organization ID required for evaluation")

    return await eval_service.evaluate_plan(organization_id, plan_data)
