"""Metadata representing a specific Execution Plan."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping


@dataclass(slots=True, frozen=True)
class PlanMetadata:
    """Core metadata describing an execution plan.

    Required
        ``id``: unique identifier for the plan.
        ``creator``: the agent or actor that generated the plan.
        ``created_at``: the timestamp when the plan was formulated.
        ``goal_description``: human-readable explanation of the plan's objective.

    Optional
        ``extensions``: namespaced extra properties not governed by the core.
    """

    id: str
    creator: str
    created_at: datetime
    goal_description: str
    extensions: Mapping[str, object] = field(default_factory=dict)
