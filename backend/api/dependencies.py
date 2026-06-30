import hashlib

from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.config import settings
from backend.application.repositories.organization_repository import UserRepository
from backend.database.session import get_db
from backend.models.models import ApiKey, Organization, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def verify_api_key_or_token(
    token: str | None = Security(oauth2_scheme),
    api_key_value: str | None = Security(api_key_header),
    x_organization_id: str | None = Header(default=None, alias="x-organization-id"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Returns a dict with 'user_id' and 'organization_id' based on authentication context.
    Supports token, API key, and graceful development fallback.
    """
    if token:
        try:
            user = await get_current_user(token=token, db=db)
            if user and user.status == "active":
                org_id = x_organization_id
                if not org_id and user.organizations:
                    org_id = user.organizations[0].id
                if not org_id:
                    res = await db.execute(select(Organization))
                    first_org = res.scalars().first()
                    org_id = first_org.id if first_org else "demo-org"
                return {"user_id": user.id, "organization_id": org_id}
        except Exception:
            pass

    if api_key_value:
        hashed_key = hashlib.sha256(api_key_value.encode()).hexdigest()
        stmt = select(ApiKey).where(ApiKey.hashed_key == hashed_key, not ApiKey.revoked)
        result = await db.execute(stmt)
        key_record = result.scalar_one_or_none()

        if key_record:
            return {"organization_id": key_record.organization_id}

    # Development & Quickstart fallback
    res = await db.execute(select(Organization))
    first_org = res.scalars().first()
    default_org = x_organization_id or (first_org.id if first_org else "demo-org")
    return {"organization_id": default_org}


from backend.application.cache.engine_cache import EngineCache
from backend.application.services.audit_service import AuditService
from backend.application.services.constitution_service import ConstitutionService
from backend.application.services.engine_manager import EngineManager
from backend.application.services.evaluation_service import EvaluationService

# Global cache instance
_engine_cache = EngineCache()
_engine_manager = EngineManager(_engine_cache)


def get_engine_manager() -> EngineManager:
    return _engine_manager


async def get_evaluation_service(
    db: AsyncSession = Depends(get_db), engine_manager: EngineManager = Depends(get_engine_manager)
) -> EvaluationService:
    return EvaluationService(db, engine_manager)


async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)


async def get_constitution_service(
    db: AsyncSession = Depends(get_db), engine_manager: EngineManager = Depends(get_engine_manager)
) -> ConstitutionService:
    return ConstitutionService(db, engine_manager)
