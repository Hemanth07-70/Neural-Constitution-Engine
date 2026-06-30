"""Plugin metadata models and capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class Capability(Enum):
    """Core capabilities a plugin can provide."""

    MATCHER = auto()
    EVALUATOR = auto()
    RESOLVER = auto()
    TRANSFORMER = auto()
    ADAPTER = auto()


@dataclass(slots=True, frozen=True)
class PluginMetadata:
    """Metadata describing a plugin."""

    id: str
    version: str
    author: str
    capabilities: tuple[Capability, ...]
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    api_version: str = "nce/v1"
