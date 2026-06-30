"""Benchmark script for the Constitution Language parser and evaluator."""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from backend.api.adapters import to_sdk_decision_request
from backend.api.schemas.evaluate import DecisionRequestSchema
from backend.core.language.evaluator import LanguageEvaluator
from backend.core.language.parser import Parser
from backend.core.language.tokens import Lexer
from backend.core.rules.context import EvaluationContext


def main():
    print("=== Constitution Language Benchmark ===")

    expr = "action.type == 'deploy' and action.params.environment == 'production' and (action.params.critical_vulns <= 0 or exists action.params.cab_approved)"

    req_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "actor": {"id": "urn:agent:devops", "type": "agent"},
        "action": {
            "type": "deploy",
            "params": {"environment": "production", "critical_vulns": 0, "cab_approved": True},
        },
        "context": {
            "constitution_id": "test",
            "constitution_version": "1.0",
            "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
            "environment": {"name": "production", "timestamp": "2026-06-29T00:00:00Z"},
        },
        "submitted_at": "2026-06-29T00:00:00Z",
    }

    req = to_sdk_decision_request(DecisionRequestSchema.model_validate(req_data))
    ctx = EvaluationContext(request=req, registry=None)

    # 1. Parsing Benchmark
    ITERATIONS = 10000

    start = time.perf_counter()
    for _ in range(ITERATIONS):
        lexer = Lexer(expr)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
    end = time.perf_counter()

    parse_time = end - start
    print(f"Parsing: {ITERATIONS} iterations took {parse_time:.4f}s ({parse_time / ITERATIONS * 1000000:.2f} µs/iter)")

    # 2. Evaluation Benchmark
    evaluator = LanguageEvaluator(ctx)
    start = time.perf_counter()
    for _ in range(ITERATIONS):
        result = evaluator.evaluate(ast)
    end = time.perf_counter()

    eval_time = end - start
    print(f"Evaluation: {ITERATIONS} iterations took {eval_time:.4f}s ({eval_time / ITERATIONS * 1000000:.2f} µs/iter)")
    print(f"Final Result: {result}")


if __name__ == "__main__":
    main()
