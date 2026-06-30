import asyncio

import asyncpg


async def test():
    try:
        conn = await asyncpg.connect("postgresql://nce_user:nce_password@localhost:5434/nce_db")
        print("Connected successfully!")
        await conn.close()
    except Exception as e:
        print("Error:", e)


asyncio.run(test())
