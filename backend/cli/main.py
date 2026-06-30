"""Lightweight CLI adapter over the core engine."""

import argparse
import json
import sys
from pathlib import Path

from backend.cli.adapters import parse_request
from backend.core.constitution.loader import ConstitutionLoader
from backend.core.evaluator.pipeline import EvaluationPipeline


def handle_validate(args: argparse.Namespace) -> int:
    """Load and structurally validate a constitution, printing a summary."""
    try:
        loader = ConstitutionLoader()
        constitution = loader.load_file(args.constitution_file)

        print("\n=== Constitution Validated ===")
        print(f"ID:      {constitution.metadata.id}")
        print(f"Version: {constitution.metadata.version}")
        print(f"Author:  {constitution.metadata.author}")
        print(f"Status:  {constitution.metadata.status}")
        print(f"Rules:   {len(constitution.rules)}")
        print("==============================\n")
        return 0
    except Exception as e:
        print(f"Error validating constitution: {e}", file=sys.stderr)
        return 1


def handle_evaluate(args: argparse.Namespace) -> int:
    """Evaluate a request against a constitution."""
    try:
        loader = ConstitutionLoader()
        constitution = loader.load_file(args.constitution_file)
    except Exception as e:
        print(f"Error loading constitution: {e}", file=sys.stderr)
        return 1

    try:
        path = Path(args.request_file)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        request = parse_request(data)
    except Exception as e:
        print(f"Error loading request: {e}", file=sys.stderr)
        return 1

    try:
        pipeline = EvaluationPipeline()
        result, explanation, audit = pipeline.evaluate(request, constitution)

        print("\n=== Evaluation Complete ===")
        print(f"Decision:     {result.action.name}")
        print(f"Winning Rule: {explanation.determining_rule.id}")
        print(f"Risk Level:   {result.risk.level.name.upper()}")
        print(f"Audit ID:     {audit.id}")
        print("\nExplanation:")
        print(f"  {explanation.determining_rule.message}")
        if explanation.resolution.overridden_contenders:
            print(f"  Overrode {len(explanation.resolution.overridden_contenders)} contender(s)")
        print("===========================\n")
        return 0
    except Exception as e:
        print(f"Evaluation error: {e}", file=sys.stderr)
        return 1


def handle_explain(args: argparse.Namespace) -> int:
    """Pretty-print an existing AuditRecord JSON."""
    try:
        path = Path(args.audit_file)
        with path.open("r", encoding="utf-8") as f:
            audit_data = json.load(f)

        print("\n=== Audit Record ===")
        print(json.dumps(audit_data, indent=2))
        print("====================\n")
        return 0
    except Exception as e:
        print(f"Error reading audit record: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Neural Constitution Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Load and validate a constitution.")
    validate_parser.add_argument("constitution_file", type=str, help="Path to constitution YAML/JSON")

    # Evaluate command
    evaluate_parser = subparsers.add_parser("evaluate", help="Execute the evaluation pipeline.")
    evaluate_parser.add_argument("constitution_file", type=str, help="Path to constitution YAML/JSON")
    evaluate_parser.add_argument("request_file", type=str, help="Path to request JSON")

    # Explain command
    explain_parser = subparsers.add_parser("explain", help="Pretty-print an audit record.")
    explain_parser.add_argument("audit_file", type=str, help="Path to audit JSON")

    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "validate":
        return handle_validate(args)
    elif args.command == "evaluate":
        return handle_evaluate(args)
    elif args.command == "explain":
        return handle_explain(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
