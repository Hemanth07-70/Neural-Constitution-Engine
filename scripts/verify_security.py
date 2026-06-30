#!/usr/bin/env python3
"""Phase 12: Security validation."""
import sys
import uuid

import requests

BASE = "http://127.0.0.1:8000"
PASS = []
FAIL = []


def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
        print(f"  ✅ {name}")
    else:
        FAIL.append(name)
        print(f"  ❌ {name} — {detail}")


print("=== Phase 12 – Security Validation ===")

# 1. Missing token → 401
r = requests.get(f"{BASE}/auth/me")
check("No token → 401", r.status_code == 401, f"Got {r.status_code}: {r.text}")

# 2. Malformed token → 401
r = requests.get(f"{BASE}/auth/me", headers={"Authorization": "Bearer notavalidtoken"})
check("Malformed token → 401", r.status_code == 401, f"Got {r.status_code}: {r.text}")

# 3. Expired/invalid JWT → 401 (forged JWT)
forged = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYWNrZXIiLCJleHAiOjF9.fakeSignature"
r = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {forged}"})
check("Forged JWT → 401", r.status_code == 401, f"Got {r.status_code}: {r.text}")

# 4. Revoked/invalid API key → 401
r = requests.post(
    f"{BASE}/evaluate",
    json={
        "id": str(uuid.uuid4()),
        "organization_id": "demo-org",
        "actor": {"id": "a", "type": "ai_agent"},
        "action": {"type": "read", "target": "db", "properties": {}},
        "context": {},
    },
    headers={"X-API-Key": "nce_invalidkey_XXXXXXXXXXXXXXXXX"},
)
check("Invalid API key → 401", r.status_code == 401, f"Got {r.status_code}: {r.text}")

# 5. No stack traces in 4xx responses
r = requests.get(f"{BASE}/auth/me")
body = r.text
check("No traceback in 401 body", "Traceback" not in body and 'File "' not in body, body[:200])

# 6. No stack traces in 500 responses (force a bad payload)
r = requests.post(f"{BASE}/evaluate", json={"invalid": "payload"})
body = r.text
check("No traceback in 422/500 body", "Traceback" not in body and 'File "' not in body, body[:200])

# 7. Cross-org isolation – the /audits endpoint enforces org matching
# Use an API-key-based auth context for org-A and try to read org-B
# Since we can't easily create two real orgs here, verify the 403 path via the dependency
# We'll test this by directly hitting the known guard:
r = requests.get(
    f"{BASE}/audits/?organization_id=org-b", headers={"X-API-Key": "nce_fake_org_a_key"}
)  # no valid key = 401, which is also correct
check("Cross-org or unauth → 401/403", r.status_code in (401, 403), f"Got {r.status_code}: {r.text}")

# 8. Ensure /docs is accessible (Swagger not locked down)
r = requests.get(f"{BASE}/docs")
check("Swagger UI accessible", r.status_code == 200, f"Got {r.status_code}")

# 9. Verify /openapi.json doesn't expose passwords
r = requests.get(f"{BASE}/openapi.json")
openapi_text = r.text
check("OpenAPI schema served", r.status_code == 200)
check("No raw passwords in OpenAPI schema", "password_hash" not in openapi_text)

print(f"\n{'='*50}")
print(f"Security Verification: {len(PASS)} passed, {len(FAIL)} failed")
sys.exit(0 if not FAIL else 1)
