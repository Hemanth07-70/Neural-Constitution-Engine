import json

import requests

payload = {
    "actor": {"id": "agent-1", "type": "machine"},
    "action": {"type": "deploy", "params": {"vulns": 1}},
    "context": {"constitution_id": "quickstart", "environment": {"name": "production"}},
}

try:
    response = requests.post("http://localhost:8000/api/v1/evaluate", json=payload)
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", str(e))
