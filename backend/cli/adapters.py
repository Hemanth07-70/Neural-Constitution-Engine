"""CLI adapters for mapping JSON dictionaries to domain objects."""

import uuid
from datetime import datetime, timezone
from typing import Any

from backend.core.domain.action import Action
from backend.core.domain.context import DecisionContext, Environment
from backend.core.domain.enums import EnvironmentName, Scope
from backend.core.domain.principals import Actor
from backend.core.domain.request import DecisionRequest


def parse_request(data: dict[str, Any]) -> DecisionRequest:
    """Parse a raw dictionary into a DecisionRequest domain object."""
    actor_data = data.get("actor", {})
    actor = Actor(
        id=actor_data.get("id", "unknown"),
        type=actor_data.get("type", "human"),
        attributes=actor_data.get("attributes", {})
    )

    action_data = data.get("action", {})
    action = Action(
        type=action_data.get("type", "unknown.action"),
        params=action_data.get("params", {})
    )

    context_data = data.get("context", {})
    env_data = context_data.get("environment", {})
    
    # Parse timestamp safely
    ts_str = env_data.get("timestamp")
    if ts_str:
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except ValueError:
            ts = datetime.now(timezone.utc)
    else:
        ts = datetime.now(timezone.utc)
        
    try:
        env_name = EnvironmentName(env_data.get("name", "development"))
    except ValueError:
        env_name = EnvironmentName.DEVELOPMENT

    env = Environment(name=env_name, timestamp=ts)

    scopes = []
    for s in context_data.get("scopes", []):
        try:
            scopes.append(Scope(s))
        except ValueError:
            pass

    ctx = DecisionContext(
        constitution_id=context_data.get("constitution_id", "default"),
        constitution_version=context_data.get("constitution_version", "1.0.0"),
        environment=env,
        correlation_id=uuid.UUID(context_data.get("correlation_id", str(uuid.uuid4()))),
        scopes=tuple(scopes)
    )

    req_id = data.get("id")
    if req_id:
        req_id = uuid.UUID(req_id)
    else:
        req_id = uuid.uuid4()
        
    sub_str = data.get("submitted_at")
    if sub_str:
        try:
            sub = datetime.fromisoformat(sub_str.replace("Z", "+00:00"))
        except ValueError:
            sub = datetime.now(timezone.utc)
    else:
        sub = datetime.now(timezone.utc)

    return DecisionRequest(
        api_version=data.get("api_version", "nce/v1"),
        id=req_id,
        actor=actor,
        action=action,
        context=ctx,
        submitted_at=sub
    )
