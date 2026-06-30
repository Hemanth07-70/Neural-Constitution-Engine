"""Flagship showcase: Autonomous DevOps Governance."""

import json
import os
import sys

# Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.sdk.engine import Engine
from backend.sdk.types import PlanValidationResult


# ANSI Colors for terminal
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_banner(text: str) -> None:
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")


def print_step(title: str) -> None:
    print(f"{Colors.OKCYAN}➔ {title}{Colors.ENDC}")


def print_success(text: str) -> None:
    print(f"   {Colors.OKGREEN}✔ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    print(f"   {Colors.FAIL}✖ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    print(f"   {Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def evaluate_plan_file(engine: Engine, plan_path: str) -> None:
    print_step(f"Loading Autonomous Execution Plan: {os.path.basename(plan_path)}")
    try:
        with open(plan_path) as f:
            plan_data = json.load(f)

        from backend.api.adapters import to_sdk_execution_plan
        from backend.api.schemas.plans import ExecutionPlanSchema

        schema = ExecutionPlanSchema.model_validate(plan_data)
        plan = to_sdk_execution_plan(schema)

        print_success(f"Execution plan loaded: {plan.metadata.id} ({len(plan.nodes)} nodes)")
    except Exception as e:
        print_error(f"Failed to load execution plan: {e}")
        return

    # 3. Validate Plan DAG
    print_step("Validating Execution Plan Graph")
    try:
        validation_result: PlanValidationResult = engine.evaluate_plan(plan)
        if validation_result.is_valid:
            print_success("DAG validation successful (no cycles).")
        else:
            print_error("DAG validation failed!")
            for err in validation_result.errors:
                print_error(err)
            return
    except Exception as e:
        print_error(f"Validation exception: {e}")
        return

    # 4. Evaluate each node in topological order
    print_banner(f"Beginning Evaluation for {plan.metadata.id}")

    order = validation_result.topological_order
    for node in order:
        print_step(f"Evaluating Node: {Colors.BOLD}{node.id}{Colors.ENDC}")
        print_info(f"Action: {node.request.action.type}")

        try:
            audit_record = engine.evaluate(node.request)
            verdict = audit_record.result.action.value
            rule_id = audit_record.result.determining_rule_id

            if verdict == "allow":
                print_success(f"Decision: ALLOWED (Rule: {rule_id})")
            elif verdict == "block":
                print_error(f"Decision: BLOCKED (Rule: {rule_id})")
                print_info(f"Reason: {audit_record.explanation.determining_rule.message}")
            else:
                print_info(f"Decision: {verdict.upper()} (Rule: {rule_id})")

            print_info(f"Assessed Risk: {audit_record.result.risk.level.value.upper()}")
            print("")

            # Stop plan execution if a node blocks (simulating real pipeline behavior)
            if verdict == "block":
                print_error("Plan execution halted due to blocked node.")
                break

        except Exception as e:
            print_error(f"Failed to evaluate node: {e}")
            break


def main() -> None:
    print_banner("Neural Constitution Engine - DevOps Governance Demo")

    base_dir = os.path.dirname(__file__)
    const_path = os.path.join(base_dir, "constitution.yaml")
    plan_compliant_path = os.path.join(base_dir, "execution-plan.json")
    plan_rejected_path = os.path.join(base_dir, "execution-plan-rejected.json")

    # 1. Initialize Engine
    print_step("Initializing Governance Engine")
    try:
        engine = Engine.load(const_path)
        print_success(f"Engine initialized with constitution: {const_path}")
    except Exception as e:
        print_error(f"Failed to load constitution: {e}")
        return

    # 2. Evaluate Compliant Plan
    evaluate_plan_file(engine, plan_compliant_path)

    # 3. Evaluate Rejected Plan
    evaluate_plan_file(engine, plan_rejected_path)

    print_banner("Demo Complete")


if __name__ == "__main__":
    main()
