import asyncio
import os
import sys

from sqlalchemy import insert

# Add project root to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.auth.security import get_password_hash
from backend.database.session import async_session_maker
from backend.models.models import Organization, User, memberships_table


async def seed():
    async with async_session_maker() as session:
        # Create Admin User
        admin_user = User(
            email="admin@nce.io", password_hash=get_password_hash("admin123"), full_name="NCE Admin", status="active"
        )
        # Create Developer User
        dev_user = User(
            email="dev@nce.io", password_hash=get_password_hash("dev123"), full_name="NCE Developer", status="active"
        )

        session.add(admin_user)
        session.add(dev_user)
        await session.flush()

        # Create Demo Organization
        org = Organization(name="Demo Corporation", slug="demo-corp", owner_id=admin_user.id)

        session.add(org)
        await session.flush()

        # Add Memberships
        await session.execute(
            insert(memberships_table).values(
                [
                    {"user_id": admin_user.id, "organization_id": org.id, "role": "Admin"},
                    {"user_id": dev_user.id, "organization_id": org.id, "role": "Developer"},
                ]
            )
        )

        await session.commit()
        print("Database seeded successfully with Demo Organization and Users (admin@nce.io, dev@nce.io)")


if __name__ == "__main__":
    asyncio.run(seed())
