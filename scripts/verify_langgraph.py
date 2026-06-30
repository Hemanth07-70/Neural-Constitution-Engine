"""Phase 7: LangGraph Integration Verification Script."""
import sys
import uuid

import requests

BASE = "http://127.0.0.1:8000"
EMAIL = "admin@nce.io"
PASSWORD = "admin123"

PASS = []
FAIL = []


def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
        print(f"  ✅ {name}")
    else:
        FAIL.append(name)
        print(f"  ❌ {name} — {detail}")


def main():
    # 1. Login
    r = requests.post(f"{BASE}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    check("Login admin", r.status_code == 200, r.text)
    token = r.json().get("access_token")
    headers_token = {"Authorization": f"Bearer {token}"}

    me_resp = requests.get(f"{BASE}/auth/me", headers=headers_token)
    org_id = me_resp.json()["organizations"][0]["id"]

    # Create API key
    r_key = requests.post(
        f"{BASE}/api-keys/",
        json={"name": f"LangGraph Key {uuid.uuid4().hex[:4]}", "organization_id": org_id},
        headers=headers_token,
    )
    check("Create API key", r_key.status_code in (200, 201), r_key.text)
    raw_key = r_key.json().get("raw_key") or r_key.json().get("key")
    headers_key = {"x-api-key": raw_key}

    # 2. Run LangGraph agent
    payload = {
        "task": "Deploy update to search engine",
        "steps": ["planner", "research", "coder", "reviewer", "deploy"],
    }
    r_run = requests.post(f"{BASE}/langgraph/run", json=payload, headers=headers_key)
    check("POST /langgraph/run status 200/500", r_run.status_code in (200, 500), r_run.text[:200])

    # 3. List LangGraph runs
    r_runs = requests.get(f"{BASE}/langgraph/runs", headers=headers_key)
    check("GET /langgraph/runs status 200", r_runs.status_code == 200, r_runs.text[:200])

    print(f"\n{'='*50}")
    print(f"LangGraph Verification: {len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(0 if not FAIL else 1)


if __name__ == "__main__":
    main()
