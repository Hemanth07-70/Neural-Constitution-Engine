"""Thread safety and determinism testing script."""

import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from backend.api.adapters import to_sdk_decision_request
from backend.api.schemas.evaluate import DecisionRequestSchema
from backend.sdk.engine import Engine


def main():
    engine = Engine.load("examples/devops-governance/constitution.yaml")

    req_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "actor": {"id": "urn:agent:devops", "type": "agent"},
        "action": {
            "type": "deploy",
            "params": {
                "environment": "production",
                "critical_vulns": 0,
                "cab_approved": True,
                "maintenance_window": "active",
                "has_rollback_plan": True,
            },
        },
        "context": {
            "constitution_id": "test",
            "constitution_version": "1.0",
            "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
            "environment": {"name": "production", "timestamp": "2026-06-29T00:00:00Z"},
        },
        "submitted_at": "2026-06-29T00:00:00Z",
    }

    request = to_sdk_decision_request(DecisionRequestSchema.model_validate(req_data))

    # Baseline expected result
    baseline_result = engine.evaluate(request)
    expected_hash = f"{baseline_result.result.action.value}:{baseline_result.result.determining_rule_id}"

    THREADS = 100
    ITERATIONS_PER_THREAD = 100

    print("Starting Thread Safety Test...")
    print(f"Baseline Hash: {expected_hash}")

    results = []

    def worker():
        for _ in range(ITERATIONS_PER_THREAD):
            res = engine.evaluate(request)
            results.append(f"{res.result.action.value}:{res.result.determining_rule_id}")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for _ in range(THREADS):
            executor.submit(worker)

    print(f"Completed {len(results)} concurrent evaluations.")

    # Verify determinism
    mismatches = sum(1 for h in results if h != expected_hash)
    print(f"Mismatches (Non-deterministic results): {mismatches}")

    if mismatches > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
