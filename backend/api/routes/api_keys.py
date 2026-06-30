import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import verify_api_key_or_token
from backend.database.session import get_db
from backend.models.models import ApiKey

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


class ApiKeyCreate(BaseModel):
    name: str
    organization_id: str | None = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    created_at: datetime
    expires_at: datetime | None = None
    revoked: bool
    last_used: datetime | None = None


class ApiKeyCreatedResponse(ApiKeyResponse):
    key: str  # Only returned once!


def generate_api_key() -> tuple[str, str, str]:
    """Returns (raw_key, prefix, hashed_key)"""
    prefix = "nce_" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    secret_part = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    raw_key = f"{prefix}_{secret_part}"
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, prefix, hashed_key


@router.post("/", response_model=ApiKeyCreatedResponse)
async def create_api_key(
    req: ApiKeyCreate,
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
    db: AsyncSession = Depends(get_db),
) -> Any:
    org_id = req.organization_id or auth_context.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Organization ID required")

    raw_key, prefix, hashed_key = generate_api_key()

    api_key = ApiKey(
        name=req.name,
        hashed_key=hashed_key,
        prefix=prefix,
        organization_id=org_id,
        expires_at=datetime.utcnow() + timedelta(days=365),  # 1 year expiry
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "prefix": api_key.prefix,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "revoked": api_key.revoked,
        "last_used": api_key.last_used,
        "key": raw_key,  # Send exactly once
    }


@router.get("/", response_model=list[ApiKeyResponse])
async def list_api_keys(
    organization_id: str | None = None,
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
    db: AsyncSession = Depends(get_db),
) -> Any:
    target_org_id = organization_id or auth_context.get("organization_id")
    if not target_org_id:
        return []

    stmt = select(ApiKey).where(ApiKey.organization_id == target_org_id)
    result = await db.execute(stmt)
    keys = result.scalars().all()

    return keys


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    organization_id: str | None = None,
    auth_context: dict[str, str] = Depends(verify_api_key_or_token),
    db: AsyncSession = Depends(get_db),
) -> Any:
    target_org_id = organization_id or auth_context.get("organization_id")

    stmt = select(ApiKey).where(ApiKey.id == key_id)
    if target_org_id:
        stmt = stmt.where(ApiKey.organization_id == target_org_id)

    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    api_key.revoked = True
    await db.commit()

    return {"status": "revoked"}
