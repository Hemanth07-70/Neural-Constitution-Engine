"""The immutable seal of a decision: :class:`AuditRecord`.

See ``docs/decision-model.md`` §2.11 and ``docs/constitution-engine.md`` §5. An
``AuditRecord`` binds the frozen request, the verdict, the explanation, and full
provenance into one append-only entry, written **before** the verdict is returned
to the caller. It is the foundation of accountability and replay.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .aliases import ApiVersion, ContentHash
from .explanation import Explanation
from .provenance import Provenance
from .request import DecisionRequest
from .result import EvaluationResult


@dataclass(slots=True, frozen=True)
class AuditRecord:
    """The tamper-evident, append-only record of one complete decision.

    Required
        ``id``: unique audit-entry identifier.
        ``api_version``: the Decision Model schema version.
        ``request``: the exact, frozen input.
        ``result``: the verdict.
        ``explanation``: the rationale.
        ``provenance``: pinned model/constitution/engine/plugin versions.
        ``recorded_at``: when the record was durably written.
        ``content_hash``: hash over the canonical serialisation of this record
        (an opaque token here; serialisation is deferred).

    Optional
        ``prev_hash``: hash of the previous record, forming a tamper-evident chain.
        ``signature``: cryptographic signature over ``content_hash``.
        ``links``: ids of related records (e.g. an approval follow-up).
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Seals one :class:`~core.domain.request.DecisionRequest`, one
        :class:`~core.domain.result.EvaluationResult`, and one
        :class:`~core.domain.explanation.Explanation`. May ``link`` to other
        :class:`AuditRecord` instances.

    Invariants (documented, not enforced here)
        Append-only and immutable — never updated or deleted; written before the
        verdict is returned; ``content_hash`` matches the canonical serialisation
        and, when ``prev_hash`` is used, the chain is verifiable end-to-end.
    """

    id: UUID
    api_version: ApiVersion
    request: DecisionRequest
    result: EvaluationResult
    explanation: Explanation
    provenance: Provenance
    recorded_at: datetime
    content_hash: ContentHash
    prev_hash: ContentHash | None = None
    signature: str | None = None
    links: tuple[UUID, ...] = ()
    extensions: Mapping[str, object] = field(default_factory=dict)
