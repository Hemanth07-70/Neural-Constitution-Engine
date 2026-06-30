from dataclasses import dataclass


@dataclass
class GovernedGraphConfig:
    organization_id: str
    constitution_version: str | None = None

    strict_mode: bool = True
    audit_every_node: bool = True
    stop_on_block: bool = True
    cache_engine: bool = True
    emit_events: bool = True
