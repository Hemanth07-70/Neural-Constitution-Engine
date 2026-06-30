"""Phase 4: Constitution Lifecycle Verification Script."""
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
    check("Login seeded admin user", r.status_code == 200, r.text)
    token = r.json().get("access_token")

    headers = {"Authorization": f"Bearer {token}"}

    # Get user's org ID
    me_resp = requests.get(f"{BASE}/auth/me", headers=headers)
    orgs = me_resp.json().get("organizations", [])
    if not orgs:
        print("❌ Admin user has no organizations!")
        sys.exit(1)
    org_id = orgs[0]["id"]
    print(f"  ℹ️ Using Organization ID: {org_id}")

    yaml_content = """apiVersion: nce/v1
kind: Constitution
metadata:
  id: e2e-test-const
  version: 1.0.1
  status: published
  author: tester
  effective_date: 2026-06-29T00:00:00Z
  scope: global
resolution:
  strategy: most-restrictive-wins
  default_verdict: block
principles:
  - id: P-TEST-1
    category: test
    statement: "Test principle"
rules:
  - id: R-TEST-BLOCK
    principle: P-TEST-1
    severity: critical
    condition:
      field: action.type
      op: equals
      value: test.drop
    action:
      type: block
      message: "Test drop blocked."
"""

    # 2. Validate YAML
    files = {"file": ("constitution.yaml", yaml_content.encode("utf-8"), "application/x-yaml")}
    r_val = requests.post(f"{BASE}/validate", files=files)
    check("POST /validate 200", r_val.status_code == 200 and r_val.json().get("status") == "valid", r_val.text)

    # 3. Create / Upload Constitution
    payload = {"version": f"1.0.{uuid.uuid4().hex[:4]}", "yaml_content": yaml_content, "organization_id": org_id}
    r_create = requests.post(f"{BASE}/constitutions/", json=payload, headers=headers)
    check("POST /constitutions/ 201", r_create.status_code == 201, r_create.text)
    const_id = r_create.json().get("id") if r_create.ok else None

    # 4. List Constitutions
    r_list = requests.get(f"{BASE}/constitutions/?organization_id={org_id}", headers=headers)
    check("GET /constitutions/ 200", r_list.status_code == 200 and len(r_list.json()) > 0, r_list.text)

    # 5. Activate Constitution
    if const_id:
        r_act = requests.post(f"{BASE}/constitutions/{const_id}/activate?organization_id={org_id}", headers=headers)
        check("POST /constitutions/{id}/activate 200", r_act.status_code == 200, r_act.text)

    print(f"\n{'='*50}")
    print(f"Constitution Verification: {len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(0 if not FAIL else 1)


if __name__ == "__main__":
    main()
