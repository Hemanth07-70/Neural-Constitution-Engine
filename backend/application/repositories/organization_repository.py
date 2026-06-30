from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.models import Organization, User, memberships_table


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).options(selectinload(User.organizations)).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, user_id: str) -> User | None:
        stmt = select(User).options(selectinload(User.organizations)).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, org_id: str) -> Organization | None:
        stmt = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_slug(self, slug: str) -> Organization | None:
        stmt = select(Organization).where(Organization.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_role_in_org(self, user_id: str, org_id: str) -> str | None:
        stmt = select(memberships_table.c.role).where(
            memberships_table.c.user_id == user_id, memberships_table.c.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
