"""Closed enumerations of the Decision Model.

Only sets that the framework *fixes* are modelled as enums here. Open,
deployment-defined vocabularies (rule category, data classification, action and
resource types) are intentionally left as string aliases in :mod:`.aliases`.

Each member's *value* is the canonical lowercase wire token used in the design
documents (e.g. ``"production"``). Nothing in the domain layer relies on those
values — serialisation is deferred — but fixing them now keeps a future encoder
trivial and unambiguous.
"""

from __future__ import annotations

from enum import Enum


class ActorType(Enum):
    """The kind of principal that proposes an action.

    See ``docs/decision-model.md`` §2.3 (Actor).
    """

    AGENT = "agent"
    HUMAN = "human"
    SERVICE = "service"
    SYSTEM = "system"


class VerdictAction(Enum):
    """The single resolved outcome the engine prescribes for a request.

    This is the closed action set of ``docs/constitution-engine.md`` §8, listed
    here from least to most restrictive for reference. It is named
    ``VerdictAction`` — not ``Action`` — to stay distinct from the
    :class:`~core.domain.action.Action` *entity*, which describes the action a
    caller *proposes* rather than the verdict the engine *returns*.
    """

    ALLOW = "allow"
    WARN = "warn"
    REWRITE = "rewrite"
    REQUEST_HUMAN_APPROVAL = "request_human_approval"
    BLOCK = "block"
    ESCALATE = "escalate"


class RiskLevel(Enum):
    """The severity of a rule or the assessed risk of a decision.

    See ``docs/constitution-engine.md`` §7 and ``docs/decision-model.md`` §2.8.
    The relative ordering of levels is meaningful to the engine, but ordering
    logic is not part of the pure domain model and is therefore not defined here.
    """

    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResultStatus(Enum):
    """Whether an evaluation result is settled or awaiting a human.

    ``PENDING`` is legitimate only for the ``request_human_approval`` and
    ``escalate`` verdicts (``docs/decision-model.md`` §2.9); every other verdict
    is ``FINAL``. That invariant is documented, not enforced here.
    """

    FINAL = "final"
    PENDING = "pending"


class EnvironmentName(Enum):
    """The deployment environment in which an action would execute.

    Drives environment-sensitive rules (e.g. "no destructive DDL in production").
    See ``docs/decision-model.md`` §2.7 (Environment).
    """

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TEST = "test"


class Scope(Enum):
    """A level in the constitutional scope hierarchy.

    Ordered from broadest/most-authoritative to narrowest
    (``docs/constitution-engine.md`` §2). A narrower scope may further restrict
    but never relax a constraint imposed by a broader one.
    """

    GLOBAL = "global"
    ORGANIZATION = "organization"
    PROJECT = "project"
    SESSION = "session"
    USER = "user"


class ResolutionStrategy(Enum):
    """The conflict-resolution strategy used to pick a single winning action.

    See ``docs/constitution-engine.md`` §6. Only the default strategy is defined
    by the framework today; the type exists so a recorded decision can name the
    strategy that produced it.
    """

    MOST_RESTRICTIVE_WINS = "most-restrictive-wins"
