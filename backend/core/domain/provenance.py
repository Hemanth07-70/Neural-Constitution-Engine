"""Decision :class:`Provenance`.

The pinned versions and plugin references a decision depended on. Extracted into
its own module because it is embedded by both
:class:`~core.domain.explanation.Explanation` and
:class:`~core.domain.audit.AuditRecord`; keeping it here avoids an import cycle
between those two modules.

See ``docs/decision-model.md`` §2.10–2.11.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .aliases import ApiVersion, PluginRef, SemanticVersion


@dataclass(slots=True, frozen=True)
class Provenance:
    """Everything required to reproduce a decision exactly.

    Required
        ``model_api_version``: the Decision Model schema version in force.
        ``constitution_version``: the pinned constitution version.
        ``engine_version``: the evaluating engine version.

    Optional
        ``evaluator_plugins``: pinned ``name@version`` references for every plugin
        consulted during evaluation.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Embedded in one :class:`~core.domain.explanation.Explanation` (optional
        there) and one :class:`~core.domain.audit.AuditRecord` (required there).
    """

    model_api_version: ApiVersion
    constitution_version: SemanticVersion
    engine_version: SemanticVersion
    evaluator_plugins: tuple[PluginRef, ...] = ()
    extensions: Mapping[str, object] = field(default_factory=dict)
