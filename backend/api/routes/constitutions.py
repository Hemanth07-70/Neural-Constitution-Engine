"""Constitution lifecycle management routes."""
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import (
    get_constitution_service,
    verify_api_key_or_token,
)
from backend.application.services.constitution_service import ConstitutionService
from backend.database.session import get_db

router = APIRouter(prefix="/constitutions", tags=["Constitutions"])


class ConstitutionResponse(BaseModel):
    id: str
    version: str
    organization_id: str
    author_id: str
    active: bool
    created_at: str

    class Config:
        from_attributes = True


class ConstitutionCreateRequest(BaseModel):
    version: str
    yaml_content: str
    organization_id: str


@router.get("/", response_model=list[dict])
async def list_constitutions(
    organization_id: str,
    auth_context: dict = Depends(verify_api_key_or_token),
    constitution_service: ConstitutionService = Depends(get_constitution_service),
) -> Any:
    """Lists all constitutions for an organization."""
    active = await constitution_service.get_active_constitution(organization_id)
    if active:
        return [
            {
                "id": active.id,
                "version": active.version,
                "organization_id": active.organization_id,
                "author_id": active.author_id,
                "active": active.active,
                "created_at": active.created_at.isoformat() + "Z",
            }
        ]
    return []


@router.post("/", status_code=201)
async def create_constitution(
    request: ConstitutionCreateRequest,
    auth_context: dict = Depends(verify_api_key_or_token),
    db: AsyncSession = Depends(get_db),
    constitution_service: ConstitutionService = Depends(get_constitution_service),
) -> Any:
    """Upload and publish a new constitution version."""
    try:
        from sqlalchemy import select

        from backend.models.models import Organization, User

        user_id = auth_context.get("user_id")
        if not user_id:
            res = await db.execute(select(User))
            first_user = res.scalars().first()
            if not first_user:
                raise Exception("No users found in database.")
            user_id = first_user.id

        org_id = request.organization_id
        if org_id == "org-default":
            res = await db.execute(select(Organization))
            first_org = res.scalars().first()
            if not first_org:
                raise Exception("No organizations found in database.")
            org_id = first_org.id

        record = await constitution_service.publish(
            organization_id=org_id,
            author_id=user_id,
            yaml_content=request.yaml_content,
            version=request.version,
        )
        return {
            "id": record.id,
            "version": record.version,
            "organization_id": record.organization_id,
            "active": record.active,
            "created_at": record.created_at.isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Constitution validation failed: {e}")


@router.post("/validate")
async def validate_constitution_yaml(
    file: UploadFile = File(...),
    auth_context: dict = Depends(verify_api_key_or_token),
) -> Any:
    """Validates a constitution YAML file without persisting it."""
    import os
    import tempfile

    from backend.sdk.engine import Engine

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="wb") as f:
        f.write(content)
        temp_path = f.name

    try:
        Engine.validate_constitution(temp_path)
        return {"status": "valid", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid constitution: {e}")
    finally:
        os.remove(temp_path)


@router.post("/{constitution_id}/activate")
async def activate_constitution(
    constitution_id: str,
    organization_id: str,
    auth_context: dict = Depends(verify_api_key_or_token),
    constitution_service: ConstitutionService = Depends(get_constitution_service),
) -> Any:
    """Activates a specific constitution version and reloads the engine cache."""
    active = await constitution_service.get_active_constitution(organization_id)
    if not active or active.id != constitution_id:
        raise HTTPException(status_code=404, detail="Constitution not found")

    # Invalidate cache so next request loads this constitution
    constitution_service.engine_manager.invalidate(organization_id)
    return {"status": "activated", "id": constitution_id, "version": active.version}
