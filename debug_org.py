import asyncio

import httpx
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.api.config import settings
from backend.models.models import Organization, User, memberships_table


async def main():
    # Insert an org for our user
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as db:
        # Get user
        res = await db.execute(select(User).where(User.email == "test@example.com"))
        user = res.scalars().first()
        if not user:
            print("User not found")
            return

        org = Organization(name="Test Org", slug="test-org", owner_id=user.id)
        db.add(org)
        await db.commit()
        await db.refresh(org)

        # add membership
        await db.execute(insert(memberships_table).values(user_id=user.id, organization_id=org.id, role="admin"))
        await db.commit()
        print("Org created and membership added")

    # Now login and call /auth/me
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        res = await client.post("/auth/login", data={"username": "test@example.com", "password": "password"})
        token = res.json()["access_token"]

        res = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        print(res.status_code)
        print(res.text)


asyncio.run(main())
