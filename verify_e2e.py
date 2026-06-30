import asyncio

import httpx


async def main():
    print("Verifying E2E endpoints...")
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # Health
        resp = await client.get("/health")
        assert resp.status_code == 200, f"Health failed: {resp.text}"
        print("GET /health ✅")

        # Version
        resp = await client.get("/version")
        assert resp.status_code == 200, f"Version failed: {resp.text}"
        print("GET /version ✅")

        # Register User
        resp = await client.post(
            "/auth/register", json={"full_name": "Test User", "email": "test@example.com", "password": "password123"}
        )
        assert resp.status_code in (201, 400), f"Register failed: {resp.text}"
        print("POST /auth/register ✅")

        # Login
        resp = await client.post("/auth/login", data={"username": "test@example.com", "password": "password123"})
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        token = resp.json()["access_token"]
        print("POST /auth/login ✅")

        # Me
        resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200, f"Me failed: {resp.text}"
        print("GET /auth/me ✅")

    print("All E2E checks passed!")


if __name__ == "__main__":
    asyncio.run(main())
