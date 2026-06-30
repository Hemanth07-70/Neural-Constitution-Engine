from typing import Any

from backend.api.schemas.evaluate import DecisionRequestSchema


def state_to_decision_request(node_name: str, state: dict[str, Any]) -> DecisionRequestSchema:
    """
    Converts a LangGraph node state into a DecisionRequestSchema.
    """
    import datetime
    import uuid

    from backend.api.schemas.base import ActorType, EnvironmentName

    now = datetime.datetime.now(datetime.UTC)

    return DecisionRequestSchema(
        id=uuid.uuid4(),
        actor={
            "id": state.get("actor_id", "system"),
            "type": ActorType.SYSTEM,
            "roles": (state.get("actor_role", "agent"),),
            "attributes": {},
        },
        action={"type": node_name, "params": {k: v for k, v in state.items() if not k.startswith("_")}},
        context={
            "constitution_id": state.get("constitution_id", "default"),
            "constitution_version": state.get("constitution_version", "1.0.0"),
            "environment": {"name": EnvironmentName.DEVELOPMENT, "timestamp": now},
            "correlation_id": uuid.uuid4(),
        },
        submitted_at=now,
    )
