"""The canonical Decision Model — NCE's pure domain layer.

This package implements, as immutable, framework-independent value objects, the
entities described in ``docs/decision-model.md``. It is the shared vocabulary
every other part of NCE agrees on: the API, the evaluation pipeline, the stores,
the dashboard, and future plugins all speak in terms of these types.

Design constraints honoured by this package:

* **Pure.** Standard library only. No web framework, database, HTTP, or
  third-party import. No I/O.
* **Immutable.** Every entity is ``frozen=True, slots=True``; collections are
  tuples; maps are read-only-by-intent ``Mapping`` fields.
* **No behaviour.** No methods, no validation, no serialisation. Spec invariants
  are documented in docstrings; their enforcement is a separate layer.

Only the Decision Model entities (and the value objects they embed) live here.
Constitution-document entities — ``Constitution``, ``Rule``, ``Principle`` — are
intentionally out of scope for this milestone.
"""

from __future__ import annotations

from .action import Action
from .aliases import (
    ActionType,
    ApiVersion,
    Category,
    Classification,
    ContentHash,
    PluginRef,
    SemanticVersion,
    Urn,
)
from .audit import AuditRecord
from .context import DecisionContext, Environment
from .enums import (
    ActorType,
    EnvironmentName,
    ResolutionStrategy,
    ResultStatus,
    RiskLevel,
    Scope,
    VerdictAction,
)
from .explanation import (
    DeterminingRule,
    Explanation,
    OverriddenContender,
    Resolution,
    Verdict,
)
from .principals import Actor, Resource, Target
from .provenance import Provenance
from .request import DecisionRequest
from .result import EvaluationResult
from .risk import RiskAssessment, RiskFactor

__all__ = [
    # Type aliases (open vocabularies)
    "ActionType",
    "ApiVersion",
    "Category",
    "Classification",
    "ContentHash",
    "PluginRef",
    "SemanticVersion",
    "Urn",
    # Enumerations (closed sets)
    "ActorType",
    "EnvironmentName",
    "ResolutionStrategy",
    "ResultStatus",
    "RiskLevel",
    "Scope",
    "VerdictAction",
    # Request aggregate and its parts
    "Action",
    "Actor",
    "DecisionContext",
    "DecisionRequest",
    "Environment",
    "Resource",
    "Target",
    # Risk
    "RiskAssessment",
    "RiskFactor",
    # Result
    "EvaluationResult",
    # Explanation and its value objects
    "DeterminingRule",
    "Explanation",
    "OverriddenContender",
    "Resolution",
    "Verdict",
    # Provenance and audit
    "AuditRecord",
    "Provenance",
]
