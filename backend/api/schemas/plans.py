"""Pydantic schemas for execution plans."""

import datetime
from typing import Any

from pydantic import Field

from backend.api.schemas.base import BaseSchema
from backend.api.schemas.evaluate import DecisionRequestSchema


class PlanMetadataSchema(BaseSchema):
    id: str
    creator: str
    created_at: datetime.datetime
    goal_description: str
    extensions: dict[str, Any] = Field(default_factory=dict)


class PlanNodeSchema(BaseSchema):
    id: str
    request: DecisionRequestSchema
    preconditions: tuple[str, ...] = Field(default_factory=tuple)
    postconditions: tuple[str, ...] = Field(default_factory=tuple)
    estimated_cost: dict[str, Any] | None = None
    human_approval_required: bool = False
    extensions: dict[str, Any] = Field(default_factory=dict)


class PlanEdgeSchema(BaseSchema):
    source_id: str
    target_id: str
    condition: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class ExecutionPlanSchema(BaseSchema):
    metadata: PlanMetadataSchema
    nodes: tuple[PlanNodeSchema, ...]
    edges: tuple[PlanEdgeSchema, ...] = Field(default_factory=tuple)


class PlanValidationResultSchema(BaseSchema):
    is_valid: bool
    errors: tuple[str, ...] = Field(default_factory=tuple)
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    topological_order: tuple[str, ...] = Field(default_factory=tuple)
    failed_node_id: str | None = None
    node_results: dict[str, Any] | None = None
