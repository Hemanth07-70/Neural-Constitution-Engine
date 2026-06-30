import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_evaluation_service, verify_api_key_or_token
from backend.application.services.evaluation_service import EvaluationService
from backend.database.session import get_db
from backend.integrations.langgraph.models import LangGraphRunRecord
from backend.models.models import AuditRecordModel

router = APIRouter(prefix="/langgraph", tags=["LangGraph Integration"])


@router.post("/run")
async def run_langgraph(
    payload: dict[str, Any],
    eval_service: EvaluationService = Depends(get_evaluation_service),
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes a predefined LangGraph agent using the governed graph integration.
    """
    organization_id = auth_context.get("organization_id")
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID required")

    # For the sake of the API, we dynamically load the example graph here
    try:
        from examples.langgraph.governed_agent import create_agent
    except ImportError:
        raise HTTPException(status_code=500, detail="Agent implementation not found in examples/langgraph")

    # Create run record
    run_id = str(uuid.uuid4())
    run_record = LangGraphRunRecord(id=run_id, organization_id=organization_id, status="running")
    db.add(run_record)
    await db.commit()

    agent = create_agent(eval_service, organization_id)

    try:
        payload["run_id"] = run_id
        # Execute the graph synchronously for this demo endpoint
        final_state = await agent.ainvoke(payload)

        # Update run record
        run_record.status = "completed"
        run_record.completed_at = datetime.utcnow()
        if "audit_ids" in final_state:
            run_record.audit_ids = final_state["audit_ids"]
        await db.commit()

        return {"run_id": run_id, "status": "completed", "state": final_state}
    except Exception as e:
        run_record.status = "failed"
        run_record.error_message = str(e)
        run_record.completed_at = datetime.utcnow()
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate")
async def evaluate_langgraph_node(
    payload: dict[str, Any],
    eval_service: EvaluationService = Depends(get_evaluation_service),
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
):
    """Standalone evaluation for a generic langgraph node."""
    organization_id = auth_context.get("organization_id")
    # Wrap it internally
    from backend.integrations.langgraph.adapters import state_to_decision_request

    request_schema = state_to_decision_request(payload.get("node_name", "unknown"), payload.get("state", {}))
    return await eval_service.evaluate_decision(organization_id, request_schema)


@router.get("/runs")
async def list_runs(
    auth_context: dict[str, str] = Depends(verify_api_key_or_token), db: AsyncSession = Depends(get_db)
):
    """Lists all LangGraph runs for the organization."""
    org_id = auth_context.get("organization_id")
    stmt = (
        select(LangGraphRunRecord)
        .where(LangGraphRunRecord.organization_id == org_id)
        .order_by(desc(LangGraphRunRecord.created_at))
        .limit(50)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/runs/{run_id}")
async def get_run(
    run_id: str, auth_context: dict[str, str] = Depends(verify_api_key_or_token), db: AsyncSession = Depends(get_db)
):
    """Gets a specific run's details."""
    org_id = auth_context.get("organization_id")
    stmt = select(LangGraphRunRecord).where(
        LangGraphRunRecord.id == run_id, LangGraphRunRecord.organization_id == org_id
    )
    result = await db.execute(stmt)
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Run not found")
    return record


@router.get("/runs/{run_id}/audit")
async def get_run_audits(
    run_id: str, auth_context: dict[str, str] = Depends(verify_api_key_or_token), db: AsyncSession = Depends(get_db)
):
    """Gets all audit records associated with a run."""
    org_id = auth_context.get("organization_id")

    run_stmt = select(LangGraphRunRecord).where(
        LangGraphRunRecord.id == run_id, LangGraphRunRecord.organization_id == org_id
    )
    run_res = await db.execute(run_stmt)
    run = run_res.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if not run.audit_ids:
        return []

    audit_stmt = (
        select(AuditRecordModel).where(AuditRecordModel.id.in_(run.audit_ids)).order_by(AuditRecordModel.recorded_at)
    )
    audit_res = await db.execute(audit_stmt)
    return audit_res.scalars().all()
