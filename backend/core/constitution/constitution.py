"""The root aggregate: Constitution."""

from __future__ import annotations

from dataclasses import dataclass

from .metadata import Metadata, Resolution
from .rule import Principle, Rule


@dataclass(slots=True, frozen=True)
class Constitution:
    """An ordered, versioned collection of principles and rules."""

    api_version: str
    kind: str
    metadata: Metadata
    principles: tuple[Principle, ...]
    rules: tuple[Rule, ...]
    resolution: Resolution | None = None
