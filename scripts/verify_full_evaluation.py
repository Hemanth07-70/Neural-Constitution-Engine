"""Full Decision Evaluation and Plan Execution Verification Script using API Key."""
import sys
import uuid
from datetime import UTC, datetime

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


def make_request(action_type: str, params: dict = None) -> dict:
    now = datetime.now(UTC).isoformat()
    return {
        "api_version": "nce/v1",
        "id": str(uuid.uuid4()),
        "actor": {"id": "urn:agent:eval-agent", "type": "agent"},
        "action": {"type": action_type, "params": params or {}},
        "context": {
            "constitution_id": "default",
            "constitution_version": "1.0",
            "environment": {"name": "production", "timestamp": now},
            "correlation_id": str(uuid.uuid4()),
        },
        "submitted_at": now,
    }


def main():
    # 1. Login as admin
    r = requests.post(f"{BASE}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    check("Login admin", r.status_code == 200, r.text)
    token = r.json().get("access_token")
    headers_token = {"Authorization": f"Bearer {token}"}

    # Get org ID
    me_resp = requests.get(f"{BASE}/auth/me", headers=headers_token)
    org_id = me_resp.json()["organizations"][0]["id"]

    # 2. Create API key for the org
    r_key = requests.post(
        f"{BASE}/api-keys/",
        json={"name": f"Eval Key {uuid.uuid4().hex[:4]}", "organization_id": org_id},
        headers=headers_token,
    )
    check("Create API key 201", r_key.status_code in (200, 201), r_key.text)
    raw_key = r_key.json().get("raw_key") or r_key.json().get("key")
    headers_key = {"x-api-key": raw_key}

    # 3. Test /evaluate
    req_eval = make_request("db.read")
    r_eval1 = requests.post(f"{BASE}/evaluate", json=req_eval, headers=headers_key)
    check("POST /evaluate status 200", r_eval1.status_code == 200, r_eval1.text)
    if r_eval1.ok:
        action = r_eval1.json().get("result", {}).get("action")
        check(
            "Evaluation returns valid action",
            action in ("allow", "block", "rewrite", "requires_approval"),
            f"Got {action}",
        )

    # 4. Test /plans/evaluate DAG
    now = datetime.now(UTC).isoformat()
    plan_payload = {
        "metadata": {
            "id": str(uuid.uuid4()),
            "creator": "urn:agent:eval-agent",
            "created_at": now,
            "goal_description": "E2E plan validation",
        },
        "nodes": [
            {"id": "n1", "request": make_request("db.read")},
            {"id": "n2", "request": make_request("db.drop")},
        ],
        "edges": [{"source_id": "n1", "target_id": "n2"}],
    }
    r_plan = requests.post(f"{BASE}/plans/evaluate", json=plan_payload, headers=headers_key)
    check("POST /plans/evaluate 200", r_plan.status_code == 200, r_plan.text)

    print(f"\n{'='*50}")
    print(f"Full Evaluation Verification: {len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(0 if not FAIL else 1)


if __name__ == "__main__":
    main()
