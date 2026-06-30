import asyncio

import httpx


async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        # Register user
        register_data = {"email": "test2@example.com", "password": "password", "full_name": "Test User 2"}
        res = await client.post("/auth/register", json=register_data)
        if res.status_code == 400 and "already exists" in res.text:
            res = await client.post("/auth/login", data={"username": "test2@example.com", "password": "password"})

        token = res.json()["access_token"]

        # Call /auth/me
        res = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        print("Status code:", res.status_code)
        print("Response:", res.text)


asyncio.run(main())
