"""Quickstart example using the Neural Constitution Engine SDK."""

import uuid
from datetime import UTC, datetime
from pathlib import Path

from backend.core.domain.enums import ActorType
from backend.sdk import Action, Actor, DecisionContext, DecisionRequest, Engine, Environment, EnvironmentName


def main() -> None:
    print(f"Neural Constitution Engine v{Engine.version()}")
    print("-" * 40)

    # Locate the example constitution
    root_dir = Path(__file__).parent.parent
    constitution_path = root_dir / "examples" / "constitution.yaml"

    # 1. Validate the constitution structurally
    is_valid = Engine.validate_constitution(constitution_path)
    print(f"Constitution is valid: {is_valid}")

    # 2. Build the Engine using the default config
    engine = Engine.load(constitution_path)
    print("Engine loaded successfully.")

    # 3. Create a DecisionRequest
    request = DecisionRequest(
        api_version="nce/v1",
        id=uuid.uuid4(),
        actor=Actor(id="agent-xyz", type=ActorType.AGENT),
        action=Action(type="db.drop", params={"table": "customers"}),
        context=DecisionContext(
            constitution_id="company-core",
            constitution_version="1.0.0",
            correlation_id=uuid.uuid4(),
            environment=Environment(name=EnvironmentName.PRODUCTION, timestamp=datetime.now(UTC)),
        ),
        submitted_at=datetime.now(UTC),
    )

    # 4. Evaluate the request
    audit = engine.evaluate(request)

    print("-" * 40)
    print(f"Action Requested: {request.action.type}")
    print(f"Decision:         {audit.result.action.name}")
    print(f"Risk Level:       {audit.result.risk.level.name.upper()}")
    print(f"Reason:           {audit.explanation.determining_rule.message}")


if __name__ == "__main__":
    main()
