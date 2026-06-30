#!/usr/bin/env python3
"""Phase 8: AI Provider validation (Ollama local)."""
import sys

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


print("=== Phase 8 – AI Provider Validation ===")

# 1. List providers
r = requests.get(f"{BASE}/providers")
check("GET /providers 200", r.status_code == 200, r.text)
if r.ok:
    providers = r.json()
    check("At least one provider registered", len(providers) > 0, str(providers))
    print(f"  ℹ️  Registered providers: {providers}")

# 2. Health check
r = requests.get(f"{BASE}/providers/health")
check("GET /providers/health 200", r.status_code == 200, r.text)
if r.ok:
    health = r.json()
    check("Health response has 'status' key", "status" in health, str(health))
    check("Health response has 'providers' key", "providers" in health, str(health))
    print(f"  ℹ️  Provider health: {health}")

# 3. List models
r = requests.get(f"{BASE}/providers/models")
check("GET /providers/models 200", r.status_code == 200, r.text[:300])
if r.ok:
    models = r.json()
    print(f"  ℹ️  Provider models: { {k: v[:2] if v else [] for k, v in models.items()} }")

# 4. Generate via Ollama (if available)
print("\n  Testing Ollama generation (may fail if Ollama not running)...")
r = requests.post(
    f"{BASE}/providers/generate",
    json={
        "provider": "ollama",
        "model": "llama3",
        "messages": [{"role": "user", "content": "Say 'hello' in exactly one word."}],
        "max_tokens": 10,
    },
    timeout=30,
)
if r.status_code == 200:
    check("POST /providers/generate Ollama 200", True)
    resp = r.json()
    print(f"  ℹ️  Ollama response: {resp.get('message', {}).get('content', '')[:100]}")
else:
    # Ollama unavailable is acceptable – verify error is graceful (not a 500 stack trace)
    body = r.text
    no_traceback = "Traceback" not in body and 'File "' not in body
    check("Ollama unavailable → graceful error (no traceback)", no_traceback, f"Status {r.status_code}: {body[:200]}")

print(f"\n{'='*50}")
print(f"Provider Verification: {len(PASS)} passed, {len(FAIL)} failed")
sys.exit(0 if not FAIL else 1)
