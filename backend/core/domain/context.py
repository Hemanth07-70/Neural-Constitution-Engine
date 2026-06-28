""":class:`Environment` and :class:`DecisionContext`.

These describe the circumstances under which an action is proposed and the policy
under which it must be judged. See ``docs/decision-model.md`` §2.2 and §2.7.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .aliases import SemanticVersion
from .enums import EnvironmentName, Scope


@dataclass(slots=True, frozen=True)
class Environment:
    """The runtime facts of execution that operational/safety rules key on.

    Required
        ``name``: the deployment environment.
        ``timestamp``: the **logical evaluation time** — the single, deterministic
        clock the engine consults. The pure domain stores it as a
        :class:`datetime.datetime`; it is expected to be timezone-aware UTC, but
        that expectation is not enforced here (validation is a separate layer).

    Optional
        ``region``, ``channel`` (e.g. ``api``, ``chat``, ``cron``),
        ``deployment_id``, ``network`` (e.g. ``internal`` / ``public``).
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Embedded in exactly one :class:`DecisionContext`.
    """

    name: EnvironmentName
    timestamp: datetime
    region: str | None = None
    channel: str | None = None
    deployment_id: str | None = None
    network: str | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class DecisionContext:
    """The policy selection and correlation context of a request.

    Pins *which constitution* governs and situates the request within a larger
    task, session, and causal chain.

    Required
        ``constitution_id``: the constitution selected to govern this request.
        ``constitution_version``: a concrete pinned version (never a range) — a
        precondition for deterministic replay.
        ``environment``: the embedded :class:`Environment`.
        ``correlation_id``: ties this request to a larger task/trace; stable
        across every request of the same logical task.

    Optional
        ``causation_id``: the immediate parent request (``None`` for a root).
        ``session_id``: groups requests in one conversation/run.
        ``scopes``: the scope levels contributing to the effective constitution.
        ``tenant_id``: the owning tenant.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Belongs to one :class:`~core.domain.request.DecisionRequest`; embeds one
        :class:`Environment`; references a constitution by id and version.
    """

    constitution_id: str
    constitution_version: SemanticVersion
    environment: Environment
    correlation_id: UUID
    causation_id: UUID | None = None
    session_id: UUID | None = None
    scopes: tuple[Scope, ...] = ()
    tenant_id: str | None = None
    extensions: Mapping[str, object] = field(default_factory=dict)
