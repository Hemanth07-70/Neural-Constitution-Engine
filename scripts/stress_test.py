"""Stress testing and profiling script."""

import os
import sys
import time

import psutil

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

    ITERATIONS = 50000

    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss / 1024 / 1024

    print(f"Starting Stress Test: {ITERATIONS} sequential evaluations...")
    start_time = time.perf_counter()

    for _ in range(ITERATIONS):
        engine.evaluate(request)

    end_time = time.perf_counter()
    end_mem = process.memory_info().rss / 1024 / 1024

    duration = end_time - start_time
    tps = ITERATIONS / duration

    print(f"Duration: {duration:.2f}s")
    print(f"Throughput: {tps:.2f} evals/sec")
    print(f"Memory Diff: {end_mem - start_mem:.2f} MB")


if __name__ == "__main__":
    main()
