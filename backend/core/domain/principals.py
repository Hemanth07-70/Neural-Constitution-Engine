"""Principals and objects of an action: :class:`Actor`, :class:`Target`, :class:`Resource`.

These three entities describe *who* proposes an action, *who* is affected by it,
and *what* is manipulated by it. See ``docs/decision-model.md`` §2.3–2.5.

All three are immutable value objects (``frozen=True, slots=True``). They are
inputs to evaluation and are never mutated by it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .aliases import Classification, Urn
from .enums import ActorType


@dataclass(slots=True, frozen=True)
class Actor:
    """The principal proposing an action.

    Typically an autonomous agent, possibly acting on behalf of a human or
    another agent. Identity here drives authorisation and the scope hierarchy.

    Required
        ``id``: stable, globally unique URN (e.g. ``agent://acme/support-bot``).
        ``type``: the kind of principal.

    Optional
        ``on_behalf_of``: the principal this actor is acting for (delegation).
        ``delegation_chain``: ordered authority chain, root authority first.
        ``roles``: roles the actor holds.
        ``attributes``: opaque, deployment-defined principal attributes.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Referenced by exactly one :class:`~core.domain.request.DecisionRequest`.
        May reference another :class:`Actor` via ``on_behalf_of``.

    Invariants (documented, not enforced here)
        ``id`` is globally unique and immutable; the ``delegation_chain`` is
        acyclic and ordered from root authority to the immediate actor.
    """

    id: Urn
    type: ActorType
    on_behalf_of: Actor | None = None
    delegation_chain: tuple[Urn, ...] = ()
    roles: tuple[str, ...] = ()
    attributes: Mapping[str, object] = field(default_factory=dict)
    extensions: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Target:
    """The principal or party affected by an action's effect.

    The "who/what is on the receiving end" — distinct from :class:`Resource`,
    which is what the action *manipulates*. For ``message.send`` the target is
    the recipient; for ``payment.send`` it is the beneficiary.

    Required
        ``id``: identifier of the affected party (URN).
        ``type``: e.g. ``user``, ``external_party``, ``agent``, ``group``.

    Optional
        ``classification``: e.g. ``internal`` / ``external`` (open vocabulary).
        ``attributes``: opaque, deployment-defined attributes.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Referenced by zero-or-one
        :class:`~core.domain.request.DecisionRequest`. When the affected party is
        another agent, ``id`` may be an :class:`Actor` URN (multi-agent case).
    """

    id: Urn
    type: str
    classification: Classification | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)
    extensions: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Resource:
    """The asset, data, or system an action reads, writes, or consumes.

    The "what is touched" — carries the data classification that privacy and
    security rules key on. Examples: a database table, a file, an API, a budget.

    Required
        ``urn``: addressable resource identifier
        (e.g. ``resource://acme/db/production.customers``).
        ``type``: e.g. ``database``, ``file``, ``api``, ``budget``.

    Optional
        ``classification``: drawn from the deployment's declared set
        (open vocabulary; see ``docs/decision-model.md`` §2.5).
        ``owner``: owning principal (URN).
        ``region``: data-residency region.
        ``attributes``: opaque, deployment-defined attributes.
        ``extensions``: namespaced data preserved but not interpreted by the core.

    Relationships
        Referenced by zero-or-one
        :class:`~core.domain.request.DecisionRequest`. Frequently the object of
        privacy, security, and cost rules.
    """

    urn: Urn
    type: str
    classification: Classification | None = None
    owner: Urn | None = None
    region: str | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)
    extensions: Mapping[str, object] = field(default_factory=dict)
