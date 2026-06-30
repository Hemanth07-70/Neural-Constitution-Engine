"""SDK Configuration."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class EngineConfig:
    """Configuration options for the Neural Constitution Engine.

    Optional
        ``plugin_dirs``: directories to scan for plugins.
        ``strict_mode``: if true, fails securely on missing configurations.
    """

    plugin_dirs: tuple[Path, ...] = field(default_factory=tuple)
    strict_mode: bool = True
