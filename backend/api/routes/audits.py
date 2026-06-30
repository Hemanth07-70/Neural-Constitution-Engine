from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_audit_service, verify_api_key_or_token
from backend.application.services.audit_service import AuditService

router = APIRouter(prefix="/audits", tags=["Audits"])


@router.get("/", response_model=list[dict[str, Any]])
async def list_audits(
    organization_id: str,
    limit: int = 50,
    offset: int = 0,
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
    audit_service: AuditService = Depends(get_audit_service),
) -> Any:
    # If using API key, ensure they can only query their own org
    if "organization_id" in auth_context and auth_context["organization_id"] != organization_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")

    # We ignore offset for now since our repo just takes limit for simplicity
    records = await audit_service.get_audits(organization_id, limit)

    # We must format it to match the expected AuditRecordSchema on the frontend
    formatted_records = []
    for r in records:
        formatted_records.append(
            {
                "id": r.id,
                "api_version": r.api_version,
                "request": r.request_data,
                "result": r.result_data,
                "explanation": r.explanation_data,
                "recorded_at": r.recorded_at.isoformat() + "Z",
            }
        )

    return formatted_records
