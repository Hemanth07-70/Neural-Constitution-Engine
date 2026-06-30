"""Immutable models for principles and rules."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class Principle:
    """A high-level governing intent."""

    id: str
    statement: str
    category: str


@dataclass(slots=True, frozen=True)
class RuleAction:
    """The prescribed outcome when a rule matches."""

    type: str
    message: str | None = None
    approver_role: str | None = None
    transform: str | None = None


@dataclass(slots=True, frozen=True)
class Rule:
    """A declarative condition over a proposal and its resulting action."""

    id: str
    condition: str | Mapping[str, object]
    action: RuleAction
    title: str | None = None
    description: str | None = None
    principle: str | Sequence[str] | None = None
    category: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    severity: str | None = None
    enabled: bool = True
    priority: int = 0
    references: tuple[str, ...] = field(default_factory=tuple)
