import asyncio

import httpx


async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Register user
        register_data = {"email": "test@example.com", "password": "password", "full_name": "Test User"}
        res = await client.post("/auth/register", json=register_data)
        if res.status_code == 400 and "already exists" in res.text:
            # Login
            res = await client.post("/auth/login", data={"username": "test@example.com", "password": "password"})

        if res.status_code != 200 and res.status_code != 201:
            print("Failed to login/register:", res.text)
            return

        token = res.json()["access_token"]
        print("Got token:", token)

        # Call /auth/me
        res = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        print("Status code:", res.status_code)
        print("Response:", res.text)


asyncio.run(main())
