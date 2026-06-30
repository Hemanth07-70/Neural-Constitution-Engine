"""Decision evaluation endpoints."""

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_evaluation_service, verify_api_key_or_token
from backend.api.schemas.evaluate import AuditRecordSchema, DecisionRequestSchema
from backend.application.services.evaluation_service import EvaluationService

router = APIRouter()


@router.post(
    "/evaluate",
    response_model=AuditRecordSchema,
    summary="Evaluate a DecisionRequest",
    description="Evaluates a single decision request against the loaded constitution.",
)
async def evaluate_decision(
    request_data: DecisionRequestSchema,
    eval_service: EvaluationService = Depends(get_evaluation_service),
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
) -> AuditRecordSchema:
    """Evaluate a decision request using the Application Layer Evaluation Service."""
    organization_id = auth_context.get("organization_id")
    if not organization_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Organization ID required for evaluation")

    return await eval_service.evaluate_decision(organization_id, request_data)
