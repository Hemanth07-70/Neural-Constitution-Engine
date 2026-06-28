"""Semantic type aliases for the Decision Model.

These are *transparent* aliases over ``str`` (PEP 695, Python 3.12). They carry
no runtime behaviour and impose no validation; their sole purpose is to make
field annotations self-documenting and to mark vocabularies that the framework
deliberately leaves **open** rather than closing into an :class:`enum.Enum`.

A value is modelled as an alias here (instead of an enum) precisely when the
design documents declare its set of legal values to be extensible or defined by
the deploying organisation — for example rule categories
(``docs/constitution-engine.md`` §4, "the category set is open") and data
classifications (``docs/decision-model.md`` §2.5, "the deployment's declared
classification set"). Encoding those as enums would contradict the documented
extensibility, so they remain strings with an intention-revealing name.
"""

# A Uniform Resource Name identifying a principal or resource, e.g.
# ``agent://acme/support-bot`` or ``resource://acme/db/production.customers``.
type Urn = str

# A dotted, namespaced action verb, e.g. ``db.execute`` or ``message.send``.
# Open by design: new action types are introduced without changing the core.
type ActionType = str

# A rule category label, e.g. ``safety`` or ``privacy``. Open by design
# (``docs/constitution-engine.md`` §4): the category taxonomy may be extended.
type Category = str

# A data-classification label, e.g. ``confidential``. Open by design: the legal
# set is declared per deployment (``docs/decision-model.md`` §2.5).
type Classification = str

# A model/schema version token for a boundary-crossing document, e.g. ``nce/v1``.
type ApiVersion = str

# A Semantic Versioning string, e.g. ``3.2.0`` (constitution / engine versions).
type SemanticVersion = str

# A content hash over a canonical serialisation, e.g. ``sha256:4f7c...``.
# Serialisation is deferred; the domain treats the hash purely as an opaque token.
type ContentHash = str

# A pinned plugin reference of the form ``name@version``, e.g. ``pii-detector@1.2.0``.
type PluginRef = str
