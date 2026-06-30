import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main():
    engine = create_async_engine("postgresql+asyncpg://nce_user:nce_password@localhost:5434/nce_db")
    with open("examples/constitution.yaml") as f:
        content = f.read()

    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE constitutions SET yaml_content = :content WHERE active = true;"), {"content": content}
        )
    print("Database updated!")


if __name__ == "__main__":
    asyncio.run(main())
