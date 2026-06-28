# The Decision Model

> **Status:** Design document. This defines the canonical data model that flows through the
> [Constitution Engine](constitution-engine.md). It realizes the input previously referred to
> as a *"Proposal"* in [`architecture.md`](architecture.md) and the
> [Constitution Engine](constitution-engine.md) design as a precise, versioned contract: the
> **DecisionRequest** and its evaluated outputs. No implementation exists yet. Where this
> document and earlier docs overlap, this document is authoritative for the *shape and
> semantics of decision data*.

## Table of contents

1. [Why a canonical decision model exists](#1-why-a-canonical-decision-model-exists)
2. [Core entities](#2-core-entities)
3. [Request lifecycle](#3-request-lifecycle)
4. [Evaluation lifecycle](#4-evaluation-lifecycle)
5. [Immutable vs mutable fields](#5-immutable-vs-mutable-fields)
6. [Identity strategy](#6-identity-strategy)
7. [Timestamps](#7-timestamps)
8. [Correlation IDs](#8-correlation-ids)
9. [Idempotency rules](#9-idempotency-rules)
10. [Serialization requirements](#10-serialization-requirements)
11. [Validation rules](#11-validation-rules)
12. [JSON examples](#12-json-examples)
13. [Entity relationship diagram](#13-entity-relationship-diagram)
14. [Why this model is future-proof](#14-why-this-model-is-future-proof)

---

## 1. Why a canonical decision model exists

Every part of NCE — the API, the evaluation pipeline, the constitution store, the audit
trail, the dashboard, and every future plugin — must agree on *what a decision is made of*.
Without one shared model, each component would invent its own representation, and the
guarantees the engine promises (determinism, explainability, replay) would dissolve at every
boundary crossing.

The Decision Model is that shared vocabulary. It exists to guarantee five things:

| Guarantee | What the canonical model provides |
| --- | --- |
| **One shape, everywhere** | A `DecisionRequest` means the same thing to the agent SDK, the engine, the audit store, and the dashboard. No translation, no drift. |
| **Determinism** | A fully-specified, normalized input is the precondition for the engine's promise that identical inputs yield identical verdicts. |
| **Replay** | Because the model captures *everything* a decision depended on — inputs, versions, context — any past decision can be re-evaluated and reproduced exactly. |
| **Explainability** | A structured, typed model lets every decision carry a structured rationale that downstream tools can render and reason about. |
| **Evolution without breakage** | A single versioned contract can be extended (new fields, new plugin data) under explicit compatibility rules, instead of N incompatible ad-hoc formats. |

The model is **deterministic** (the same data always describes the same decision),
**self-describing** (carries its own versions and identity), and **closed at the core but
open at the edges** (a fixed trusted core plus namespaced extension points — see §14).

---

## 2. Core entities

The model is a composition. A **DecisionRequest** is the root aggregate; the engine consumes
it and produces a **RiskAssessment**, an **EvaluationResult**, an **Explanation**, and finally
an **AuditRecord** that binds them all together immutably.

Two structural conventions apply to **every** entity:

- Every entity that crosses a boundary carries a stable `id` (§6) and is independently
  serializable (§10).
- Every entity may carry an `extensions` map: a reverse-DNS-namespaced container for data the
  trusted core does not interpret but must preserve (§14). Core evaluation never trusts
  `extensions`; only allow-listed plugins read their own namespace.

### 2.1 DecisionRequest

**Purpose.** The root input to the engine: a complete, self-contained description of one
action an actor proposes to take, in a given context, awaiting a verdict. It is the unit of
evaluation, of idempotency, and of audit.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `apiVersion` | string | Model schema version, e.g. `nce/v1` (§10). |
| `id` | UUIDv7 | Unique request id (§6). |
| `actor` | Actor | Who proposes the action. |
| `action` | Action | What is proposed. |
| `context` | DecisionContext | Where/when/under what policy (embeds Environment). |
| `submitted_at` | RFC 3339 | Client-asserted submission time (§7). |

**Optional fields.** `target` (Target), `resource` (Resource), `idempotency_key` (string,
§9), `extensions` (map). At least **one** of `target` or `resource` MUST be present
(invariant below).

**Relationships.** Composes exactly one `Actor`, one `Action`, one `DecisionContext`; composes
zero-or-one `Target` and zero-or-one `Resource`. Is referenced by exactly one
`EvaluationResult` and exactly one `AuditRecord`.

**Invariants.**
- `id` is unique and immutable for the life of the request.
- At least one of `{target, resource}` is present (an action with neither subject nor object
  is not evaluable).
- Once submitted, a DecisionRequest is **immutable** (§5). Corrections are new requests, not
  edits.
- All referenced ids (actor, resource) must be resolvable or self-describing; dangling
  references fail validation (fail-closed).

### 2.2 DecisionContext

**Purpose.** The circumstances under which the action is proposed and the policy under which
it must be judged. It pins *which constitution* governs and *which run* this belongs to.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `constitution_id` | string | The constitution selected to govern this request. |
| `constitution_version` | SemVer | Pinned version (§ versioning, constitution-engine §10). |
| `environment` | Environment | Runtime facts (embedded). |
| `correlation_id` | UUIDv7 | Ties this request to a larger task/trace (§8). |

**Optional fields.** `session_id` (UUIDv7), `causation_id` (UUIDv7, the immediate parent
request, §8), `scopes` (list of scope identifiers contributing to the effective
constitution, per constitution-engine §2), `tenant_id`, `extensions`.

**Relationships.** Belongs to one `DecisionRequest`; embeds one `Environment`. References a
`Constitution` (by id+version) held in the constitution store.

**Invariants.**
- `constitution_version` is a concrete pinned version, never a floating range — replay
  demands it.
- `correlation_id` is stable across all requests of the same logical task.
- `causation_id`, when present, references a real prior request (or is null for a root
  request).

### 2.3 Actor

**Purpose.** The principal proposing the action — typically an autonomous agent, possibly
acting on behalf of a human or another agent. Identity here drives authorization and the
scope hierarchy.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `id` | URN | Stable principal identifier, e.g. `agent://acme/support-bot`. |
| `type` | enum | `agent` \| `human` \| `service` \| `system`. |

**Optional fields.** `on_behalf_of` (Actor reference — delegation), `delegation_chain` (ordered
list of Actor ids, for multi-agent provenance — §14), `roles` (list), `attributes` (map),
`extensions`.

**Relationships.** Referenced by one `DecisionRequest`. May reference another `Actor` via
`on_behalf_of`, forming a delegation chain (acyclic).

**Invariants.**
- `id` is globally unique and immutable.
- `delegation_chain` is acyclic and ordered from root authority to immediate actor.
- An `Actor` is never mutated by evaluation; it is an input fact.

### 2.4 Target

**Purpose.** The **principal or party affected by the action's effect** — the "who/what is on
the receiving end." Distinct from Resource (which is *what is manipulated*). Example: for
`message.send`, the Target is the recipient; for `payment.send`, the Target is the
beneficiary.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `id` | URN | Identifier of the affected party. |
| `type` | string | e.g. `user`, `external_party`, `agent`, `group`. |

**Optional fields.** `attributes` (map — e.g. `{ "relationship": "third_party" }`),
`classification` (e.g. `internal` \| `external`), `extensions`.

**Relationships.** Referenced by zero-or-one `DecisionRequest`. May itself be an `Actor` id
when the target is another agent (multi-agent — §14).

**Invariants.**
- If present, `id` and `type` are required together.
- A request with neither `target` nor `resource` is invalid (see 2.1).

### 2.5 Resource

**Purpose.** The **asset, data, or system the action reads, writes, or consumes** — the "what
is touched." Carries the data classification that privacy/security rules key on. Example: a
database table, a file, an API endpoint, a budget.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `urn` | URN | Addressable resource identifier, e.g. `resource://acme/db/production.customers`. |
| `type` | string | e.g. `database`, `file`, `api`, `budget`, `message_channel`. |

**Optional fields.** `classification` (e.g. `public` \| `internal` \| `confidential` \|
`restricted`), `owner`, `attributes` (map), `region`, `extensions`.

**Relationships.** Referenced by zero-or-one `DecisionRequest`. Frequently the object of
privacy/security/cost rules in the constitution.

**Invariants.**
- `urn` is unique within its naming authority and stable.
- `classification`, when present, is drawn from the deployment's declared classification set;
  unknown values fail validation rather than being silently accepted.

### 2.6 Action

**Purpose.** The verb and parameters of what the actor proposes to do. This is the primary
subject of rule conditions in the constitution.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `type` | string | Dotted action verb, e.g. `db.execute`, `message.send`, `payment.send`. |
| `params` | object | Action-specific parameters (typed per action type). |

**Optional fields.** `intent` (free-text rationale supplied by the agent, advisory only),
`estimated_cost` (object — for cost rules), `extensions`.

**Relationships.** Composed by one `DecisionRequest`. Read by the engine's matching stage; may
be transformed by a `rewrite` action into a derived action recorded in the EvaluationResult.

**Invariants.**
- `type` is a non-empty, namespaced verb.
- `params` is a flat-or-nested object validated against the schema registered for `type`
  (unknown `type` → validation failure, fail-closed).
- `intent` is **never** trusted for authorization — it is advisory metadata only. The engine
  governs the action, not the agent's stated reason for it.

### 2.7 Environment

**Purpose.** The runtime facts of execution that operational/safety rules key on — *where* and
*under what conditions* the action would occur.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `name` | enum | `production` \| `staging` \| `development` \| `test`. |
| `timestamp` | RFC 3339 | **The logical evaluation time** — the deterministic clock (§7). |

**Optional fields.** `region`, `channel` (e.g. `api`, `chat`, `cron`), `deployment_id`,
`network` (e.g. `internal` \| `public`), `extensions`.

**Relationships.** Embedded in exactly one `DecisionContext`.

**Invariants.**
- `timestamp` is the single source of "now" for evaluation; the engine uses no other clock for
  rule decisions (determinism, constitution-engine §5).
- `name` governs environment-sensitive rules (e.g. "no destructive DDL in production").

### 2.8 RiskAssessment

**Purpose.** The engine's structured judgement of *how dangerous* the proposal is, independent
of the action taken. Produced during evaluation; consumed by the EvaluationResult and the
explanation.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `level` | enum | `informational` \| `low` \| `medium` \| `high` \| `critical` (constitution-engine §7). |
| `determined_by` | string | What set the level (e.g. winning rule id, or `aggregate`). |

**Optional fields.** `score` (normalized 0–1, optional quantitative signal), `factors` (list
of `{ rule_id, category, severity, note }` contributing entries), `extensions`.

**Relationships.** Produced from the matched rule set; referenced by one `EvaluationResult` and
surfaced in the `Explanation`.

**Invariants.**
- `level` equals the highest severity among contributing rules (descriptive, not prescriptive
  — the *action* is decided separately by conflict resolution).
- `score`, when present, is monotonic with `level` (a `critical` is never scored below a
  `high`).

### 2.9 EvaluationResult

**Purpose.** The **verdict**: the single resolved action the engine prescribes for the
request, plus everything needed to act on and understand it.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUIDv7 | Result id. |
| `request_id` | UUIDv7 | The DecisionRequest evaluated. |
| `action` | enum | `allow` \| `warn` \| `rewrite` \| `request_human_approval` \| `block` \| `escalate` (constitution-engine §8). |
| `risk` | RiskAssessment | Embedded risk judgement. |
| `status` | enum | `final` \| `pending` (pending only for `request_human_approval`/`escalate` awaiting resolution). |
| `decided_at` | RFC 3339 | Engine decision time (§7). |

**Optional fields.** `transformed_action` (Action — present iff `action == rewrite`),
`warnings` (list of advisory notes), `determining_rule_id` (string), `extensions`.

**Relationships.** Belongs to one `DecisionRequest`; embeds one `RiskAssessment`; is explained
by one `Explanation`; is sealed into one `AuditRecord`. A `pending` result may be *superseded*
by a linked follow-up result (the human's decision) — never mutated in place (§5).

**Invariants.**
- `action` is exactly one of the six closed action types.
- `transformed_action` is present **if and only if** `action == rewrite`.
- `status == pending` only for `request_human_approval` or `escalate`; all other verdicts are
  `final`.
- The result is deterministic for a given (request, effective-constitution, engine-version).

### 2.10 Explanation

**Purpose.** The human- and machine-readable rationale for the verdict. Mandatory for **every**
result, including `allow`. This is the concrete structure introduced in constitution-engine §9.

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `decision_id` | UUIDv7 | Links to the EvaluationResult/AuditRecord. |
| `verdict` | object | `{ action, risk_level }` mirror of the result. |
| `determining_rule` | object | id, title, scope, category, severity, principle, statement, message. |
| `resolution` | object | strategy, `decided_by` criterion, `overridden_contenders[]` with reasons (constitution-engine §6). |

**Optional fields.** `warnings` (list), `applied_transforms` (list of `name@version`),
`references` (list), `provenance` (constitution id+version, engine version, evaluator plugin
`name@version` list), `extensions`.

**Relationships.** Explains exactly one `EvaluationResult`; embedded in the `AuditRecord`.

**Invariants.**
- Exists for every result without exception.
- Names the determining rule and *why* contenders lost (traceable & complete).
- Identical inputs produce byte-identical explanations under canonical serialization (§10).

### 2.11 AuditRecord

**Purpose.** The immutable, tamper-evident sealing of one complete decision: the request, the
result, the explanation, and the full provenance — written **before** the verdict is returned
to the caller (constitution-engine §5).

**Required fields.**

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUIDv7 | Audit entry id. |
| `request` | DecisionRequest | The exact, frozen input. |
| `result` | EvaluationResult | The verdict. |
| `explanation` | Explanation | The rationale. |
| `provenance` | object | `constitution_version`, `engine_version`, `evaluator_plugins[]`, `model_apiVersion`. |
| `recorded_at` | RFC 3339 | When the record was durably written (§7). |
| `content_hash` | string | Hash of the canonical serialization of this record (§10). |

**Optional fields.** `prev_hash` (string — hash of the previous record, forming a tamper-evident
chain), `signature` (cryptographic signature over `content_hash`), `links` (ids of related
records, e.g. the human-approval follow-up), `extensions`.

**Relationships.** Seals one `DecisionRequest` + one `EvaluationResult` + one `Explanation`.
May `link` to other AuditRecords (approval follow-ups, escalations, multi-step tasks via
`correlation_id`).

**Invariants.**
- **Append-only and immutable.** Never updated or deleted. State changes (e.g. an approval
  arriving) are *new linked records*, not edits.
- Written **before** the corresponding verdict is returned (no unrecorded allow can occur).
- `content_hash` matches the canonical serialization; if `prev_hash` is used, the chain is
  verifiable end-to-end.

---

## 3. Request lifecycle

The lifecycle of a `DecisionRequest` from creation to acceptance for evaluation. (Evaluation
itself is §4.)

```
 ┌──────────┐   ┌───────────┐   ┌────────────┐   ┌───────────┐   ┌───────────┐
 │ CONSTRUCT│──▶│  SUBMIT   │──▶│  VALIDATE  │──▶│  RESOLVE  │──▶│  ACCEPTED │
 │ (by agent)│  │ (to API)  │   │ (schema +  │   │ idempotency│  │ (frozen,  │
 │           │  │           │   │  semantic) │   │  + dedupe  │   │ immutable)│
 └──────────┘   └───────────┘   └─────┬──────┘   └─────┬─────┘   └─────┬─────┘
                                      │ invalid        │ duplicate     │
                                      ▼                ▼               ▼
                                 ┌─────────┐    ┌──────────────┐  ┌─────────────┐
                                 │ REJECTED│    │ RETURN PRIOR │  │ → EVALUATION │
                                 │ (block, │    │  RESULT (§9) │  │    (§4)      │
                                 │ audited)│    └──────────────┘  └─────────────┘
                                 └─────────┘
```

1. **Construct.** The agent assembles a `DecisionRequest` (actor, action, target/resource,
   context). It mints `id` and `correlation_id`/`causation_id` and may attach an
   `idempotency_key`.
2. **Submit.** The request is sent to the API layer and authenticated.
3. **Validate.** Structural (schema), referential (ids resolve), and semantic (invariants)
   validation. Failure → `REJECTED` as an audited `block` (fail-closed).
4. **Resolve idempotency.** If `idempotency_key` matches a prior request (§9), return the
   prior result without re-evaluating or duplicating side-effects.
5. **Accepted.** The request is **frozen and immutable**. It now enters the evaluation
   lifecycle.

---

## 4. Evaluation lifecycle

This mirrors the engine pipeline (constitution-engine §5) and shows which entities each stage
produces. Deterministic and ordered throughout.

```
 ACCEPTED REQUEST
        │
        ▼
 (1) RESOLVE effective constitution  ──► uses DecisionContext (id + version + scopes)
        │
        ▼
 (2) NORMALIZE request                ──► canonical DecisionRequest (stable form, §10)
        │
        ▼
 (3) MATCH rules                       ──► matched-rule set  (evaluator plugins may run, §14)
        │
        ▼
 (4) ASSESS risk                       ──► RiskAssessment
        │
        ▼
 (5) RESOLVE conflicts                  ──► single winning action  (constitution-engine §6)
        │
        ▼
 (6) DECIDE                            ──► EvaluationResult (+ transformed_action if rewrite)
        │
        ▼
 (7) EXPLAIN                           ──► Explanation
        │
        ▼
 (8) SEAL  (append BEFORE returning)   ──► AuditRecord (content_hash, prev_hash)
        │
        ▼
 RETURN EvaluationResult + Explanation to caller
```

For a `pending` verdict (`request_human_approval` / `escalate`), the sealed AuditRecord
records the request; when the human resolves it, a **new** linked AuditRecord captures the
outcome, and the original EvaluationResult is superseded (never mutated). The
`correlation_id` ties the chain together for replay and reporting.

---

## 5. Immutable vs mutable fields

The model is **immutable by default**. State evolves by appending new, linked records — never
by editing existing ones. This is what makes audit replay sound.

| Entity | Immutable once… | Mutable / evolving |
| --- | --- | --- |
| `DecisionRequest` | accepted (§3) | *Nothing.* Corrections are new requests. |
| `DecisionContext`, `Actor`, `Target`, `Resource`, `Action`, `Environment` | request accepted | Nothing (they are frozen inputs). |
| `RiskAssessment` | produced | Nothing. |
| `EvaluationResult` | sealed | `status` conceptually transitions `pending → resolved`, but this is realized as a **new linked result/record**, not an in-place edit. |
| `Explanation` | produced | Nothing. |
| `AuditRecord` | written | **Never** — strictly append-only; deletions are forbidden. |

Rule of thumb: **if you want to "change" a decision, you create a new one that references the
old.** The only legitimate write to historical data is appending a record that links to it.

---

## 6. Identity strategy

| Concern | Strategy | Rationale |
| --- | --- | --- |
| **Entity ids** (`id`) | **UUIDv7** | Globally unique without coordination (works in distributed/multi-agent settings); time-ordered prefix gives natural sortability and index locality. |
| **Principals & resources** | **URN-style** (`agent://…`, `resource://…`) | Human-legible, hierarchical, namespace-able per tenant/authority; stable and meaningful in audits. |
| **Action types** | **Dotted namespaced verbs** (`db.execute`) | Readable, groupable, collision-resistant across plugins. |
| **Idempotency** | caller-supplied `idempotency_key` (opaque string) | Lets clients safely retry (§9). |
| **Content identity** | `content_hash` over canonical form (§10) | Tamper-evidence and deduplication independent of assigned ids. |

Principles: ids are **assigned at the point of creation** by whoever creates the entity (agent
for requests, engine for results/records); ids are **opaque and immutable**; the model never
relies on a central id authority, so it scales to distributed generation.

---

## 7. Timestamps

All timestamps are **RFC 3339 / ISO 8601, UTC, with explicit offset (`Z`)**, to at least
millisecond precision. The model distinguishes **logical time** from **observed time**:

| Field | Source | Meaning | Used for |
| --- | --- | --- | --- |
| `environment.timestamp` | client-asserted | **The logical "now"** for evaluation. | **Rule decisions** — the *only* clock the engine consults, preserving determinism & replay. |
| `request.submitted_at` | client-asserted | When the agent submitted. | Provenance, ordering hints. |
| `result.decided_at` | engine-observed | When the verdict was produced. | Latency metrics, provenance. |
| `audit.recorded_at` | engine-observed | When the record was durably written. | Compliance, ordering of the audit log. |

Critical rule: **evaluation never reads the host wall-clock.** Any time-sensitive rule
("inside the change-freeze window") evaluates against `environment.timestamp`, supplied on the
request. This is what allows a decision to be replayed years later and reach the identical
verdict.

---

## 8. Correlation IDs

Three identifiers situate a request within a larger process. All are UUIDv7.

| Field | Scope | Purpose |
| --- | --- | --- |
| `correlation_id` | A whole logical task / trace | Groups every request belonging to one agent task or workflow, possibly spanning many agents and steps. Stable across the entire task. |
| `causation_id` | Immediate parent | The `id` of the request that *directly caused* this one. Builds the causal tree; null for a root request. |
| `session_id` | A conversation / run | Groups requests in one interactive or execution session (maps to the *session scope* in constitution-engine §2). |

Together these let the audit trail reconstruct **what happened, in what order, caused by
what** — essential for multi-agent orchestration (§14) and forensic replay. `correlation_id`
is the join key across distributed components; `causation_id` is the edge in the causal DAG.

---

## 9. Idempotency rules

Distributed callers retry. Idempotency ensures retries neither produce duplicate audit records
nor trigger duplicate side-effects (e.g. a second `escalate` alert).

1. A caller MAY attach an `idempotency_key` to a `DecisionRequest`.
2. The key is scoped to `(tenant_id, actor.id, idempotency_key)` within a configured **TTL
   window**.
3. **Same key + identical request payload** → the engine returns the **original
   EvaluationResult** and does **not** re-evaluate, re-seal, or re-fire side-effects.
4. **Same key + different payload** (by `content_hash`) → a **conflict** error (fail-closed);
   the engine refuses to overload one key with two meanings.
5. **No key** → every submission is treated as distinct (still deterministic, but a new audit
   record is written each time).
6. Idempotency is an **optimization and a safety net, not a correctness crutch**: because
   evaluation is already deterministic, replaying the same input yields the same verdict
   regardless — idempotency exists to suppress duplicate *records and effects*.

---

## 10. Serialization requirements

| Requirement | Rule |
| --- | --- |
| **Wire format** | JSON (UTF-8). The model is JSON-first; other encodings must round-trip losslessly. |
| **Canonical form** | A canonical JSON serialization (per a JCS-style profile: lexicographically ordered keys, no insignificant whitespace, normalized number/string forms) is defined for **hashing, signing, and equality**. |
| **Determinism** | The canonical form is byte-stable: identical logical content → identical bytes → identical `content_hash`. |
| **Schema versioning** | Every top-level document carries `apiVersion` (e.g. `nce/v1`). The engine refuses (fail-closed) any `apiVersion` it does not understand. |
| **Unknown fields** | Unknown top-level/core fields are **rejected** in validation (strict core). Unknown data under a namespaced `extensions` key is **preserved verbatim** through serialization and audit but **ignored by core evaluation** (§14). |
| **Forward/backward compat** | Round-tripping a document through an engine that doesn't understand a particular `extensions` namespace must not corrupt or drop it. |
| **Stability of hashes** | `content_hash` is computed over the canonical form; it is reproducible by any conforming implementation, enabling cross-system tamper checks and the optional `prev_hash` chain. |

Determinism + canonical serialization are jointly the foundation of replay and tamper-evidence:
the same decision re-serialized anywhere yields the same bytes and the same hash.

---

## 11. Validation rules

Validation is layered and **fail-closed**: a request that cannot be fully validated is
rejected as an audited `block`, never evaluated on a guess.

1. **Structural.** Conforms to the `apiVersion` schema: required fields present, types correct,
   enums in range, no unknown core fields, timestamps RFC 3339.
2. **Referential.** All ids are well-formed; referenced `constitution_id@version` resolves in
   the store; `causation_id`/`on_behalf_of` reference real entities or are null; `delegation_chain`
   is acyclic.
3. **Semantic / invariant.** All entity invariants from §2 hold — notably: at least one of
   `{target, resource}`; `transformed_action` present iff `rewrite`; `status == pending` only
   for approval/escalate; `action.type` has a registered parameter schema and `params`
   conforms; `classification` values are from the declared set.
4. **Authorization.** The authenticated caller is permitted to submit on behalf of `actor`,
   and (for constitution-editing operations, out of scope here) is privileged accordingly.
5. **Idempotency.** Apply §9 conflict checks.

Each failed layer produces a structured rejection naming the offending field and rule, so
clients can correct deterministically. Rejections are themselves audited.

---

## 12. JSON examples

### 12.1 A complete DecisionRequest

```json
{
  "apiVersion": "nce/v1",
  "id": "018f9c2a-7b3e-7e21-9a44-0d1e2f3a4b5c",
  "actor": {
    "id": "agent://acme/support-bot",
    "type": "agent",
    "on_behalf_of": { "id": "user://acme/jane.doe", "type": "human" },
    "roles": ["support-agent"]
  },
  "action": {
    "type": "db.execute",
    "params": {
      "statement": "DELETE FROM customers WHERE id = 4821",
      "record_count": 1
    },
    "intent": "Honor a customer's right-to-erasure request."
  },
  "target": {
    "id": "user://acme/customer/4821",
    "type": "user",
    "classification": "external"
  },
  "resource": {
    "urn": "resource://acme/db/production.customers",
    "type": "database",
    "classification": "restricted",
    "region": "eu-west-1"
  },
  "context": {
    "constitution_id": "org.acme.support-agent",
    "constitution_version": "3.2.0",
    "correlation_id": "018f9c2a-1111-7e21-9a44-aaaaaaaaaaaa",
    "causation_id": null,
    "session_id": "018f9c2a-2222-7e21-9a44-bbbbbbbbbbbb",
    "scopes": ["global", "organization", "project", "session", "user"],
    "tenant_id": "acme",
    "environment": {
      "name": "production",
      "timestamp": "2026-06-28T14:31:00.000Z",
      "region": "eu-west-1",
      "channel": "chat"
    }
  },
  "idempotency_key": "erasure-req-4821-v1",
  "submitted_at": "2026-06-28T14:31:00.120Z",
  "extensions": {
    "com.acme.ticketing": { "ticket_id": "SUP-99812" }
  }
}
```

### 12.2 The resulting EvaluationResult

```json
{
  "apiVersion": "nce/v1",
  "id": "018f9c2a-9aaa-7e21-9a44-0d1e2f3a4b5c",
  "request_id": "018f9c2a-7b3e-7e21-9a44-0d1e2f3a4b5c",
  "action": "request_human_approval",
  "status": "pending",
  "risk": {
    "level": "high",
    "determined_by": "R-FIN-DATA-ERASURE",
    "score": 0.78,
    "factors": [
      { "rule_id": "R-FIN-DATA-ERASURE", "category": "compliance", "severity": "high",
        "note": "Irreversible deletion of restricted production data." }
    ]
  },
  "determining_rule_id": "R-FIN-DATA-ERASURE",
  "warnings": [],
  "decided_at": "2026-06-28T14:31:00.140Z"
}
```

### 12.3 The sealed AuditRecord (abridged)

```json
{
  "apiVersion": "nce/v1",
  "id": "018f9c2a-bbbb-7e21-9a44-0d1e2f3a4b5c",
  "request": { "id": "018f9c2a-7b3e-7e21-9a44-0d1e2f3a4b5c", "...": "frozen request" },
  "result": { "id": "018f9c2a-9aaa-7e21-9a44-0d1e2f3a4b5c", "action": "request_human_approval" },
  "explanation": {
    "decision_id": "018f9c2a-9aaa-7e21-9a44-0d1e2f3a4b5c",
    "verdict": { "action": "request_human_approval", "risk_level": "high" },
    "determining_rule": {
      "id": "R-FIN-DATA-ERASURE",
      "scope": "organization",
      "category": "compliance",
      "severity": "high",
      "principle": "P-DATA-LIFECYCLE",
      "statement": "Irreversible deletion of restricted data requires human authorization.",
      "message": "Erasure of restricted production records requires a data-steward approval."
    },
    "resolution": {
      "strategy": "most-restrictive-wins",
      "decided_by": "action-authority",
      "overridden_contenders": [
        { "id": "R-USER-AUTONOMY", "scope": "user", "action": "allow", "reason": "lower authority" }
      ]
    }
  },
  "provenance": {
    "model_apiVersion": "nce/v1",
    "constitution_version": "3.2.0",
    "engine_version": "0.1.0",
    "evaluator_plugins": []
  },
  "recorded_at": "2026-06-28T14:31:00.150Z",
  "prev_hash": "sha256:9b1e…",
  "content_hash": "sha256:4f7c…"
}
```

---

## 13. Entity relationship diagram

```
                                ┌────────────────────────────────┐
                                │        DecisionRequest          │
                                │  id · apiVersion · submitted_at  │
                                │  idempotency_key · extensions    │
                                └───┬───────┬───────┬───────┬─────┘
                  composes 1        │       │       │       │  composes 0..1
        ┌──────────────────────────┘       │       │       └────────────────────┐
        ▼                                   ▼       ▼                            ▼
 ┌─────────────┐                     ┌───────────┐ ┌───────────┐         ┌──────────────┐
 │    Actor    │                     │  Action   │ │  Target   │         │   Resource   │
 │ id · type   │                     │ type·params│ │ id · type │         │ urn · type   │
 │ on_behalf_of├──┐ delegation       └───────────┘ └─────┬─────┘         │ classification│
 └─────────────┘  │ (self-ref)                           │ may be an     └──────────────┘
        ▲         └──────────────────────────────────────┘ Actor (agent)
        │ references
        │                          ┌──────────────────────────────┐
        │                          │       DecisionContext         │  composes 1
        └──────────────────────────┤ constitution_id · version     │◀──────────┐
                                    │ correlation_id · causation_id │           │
                                    │ session_id · scopes           │           │
                                    └──────────────┬────────────────┘           │
                                       embeds 1     │                            │
                                                    ▼                            │
                                            ┌───────────────┐                    │
                                            │  Environment  │                    │
                                            │ name·timestamp│                    │
                                            └───────────────┘                    │
                                                                                 │
   ENGINE PRODUCES ▼                                                             │
 ┌─────────────────────┐  embeds 1   ┌──────────────────┐                       │
 │  EvaluationResult    │────────────▶│  RiskAssessment  │                       │
 │ id · request_id ─────┼─────────────┼─ references ─────┼───────────────────────┘
 │ action · status      │             │ level · score    │
 │ transformed_action   │             └──────────────────┘
 └─────────┬───────────┘
           │ explained by 1
           ▼
 ┌─────────────────────┐
 │     Explanation      │
 │ determining_rule     │
 │ resolution           │
 └─────────┬───────────┘
           │ sealed into 1
           ▼
 ┌──────────────────────────────────────────────────────────┐
 │                       AuditRecord                          │
 │  id · request · result · explanation · provenance          │
 │  recorded_at · content_hash · prev_hash · links[] ─────────┼──▶ links to other
 │  (APPEND-ONLY, IMMUTABLE)                                  │     AuditRecords
 └──────────────────────────────────────────────────────────┘
```

---

## 14. Why this model is future-proof

The model is designed so that the four hardest directions of growth do **not** require
breaking changes to the trusted core.

### Plugins
- The `extensions` map (every entity) is a **namespaced, preserved, core-ignored** container.
  A plugin attaches data under `com.vendor.feature` without any schema change; the core neither
  trusts nor drops it (§10).
- Evaluator and transform plugins (constitution-engine §11) appear in the model only as
  *recorded provenance* (`evaluator_plugins: [name@version]`). Adding a plugin changes behavior
  only for constitutions that reference it, and every decision records exactly which plugins
  ran — so plugin-influenced decisions remain reproducible.

### Multi-agent orchestration
- `Actor.on_behalf_of` and `Actor.delegation_chain` capture *who authorized whom*, so a
  decision made by a sub-agent retains the full chain of authority.
- A `Target` may itself be an agent, modelling agent-to-agent actions natively.
- `correlation_id` (the task), `causation_id` (the causal edge), and `session_id` (the run)
  reconstruct the entire multi-agent causal DAG from the audit trail alone (§8).

### Distributed execution
- **UUIDv7** ids are generated without coordination, so any node mints valid ids concurrently.
- **Idempotency keys** (§9) make retries across an unreliable network safe — no duplicate
  records or side-effects.
- **No shared mutable state**: every entity is immutable once created; "changes" are new linked
  records (§5). There is nothing to lock or to race on.
- **Canonical serialization + `content_hash`** (§10) give a coordination-free way to detect
  divergence and dedupe identical decisions across nodes.

### Audit replay
- The model captures **everything a decision depended on**: the frozen request, the pinned
  `constitution_version`, the `engine_version`, the plugin versions, and the **logical clock**
  (`environment.timestamp`, never the host wall-clock — §7).
- Combined with the engine's determinism, this means any historical `AuditRecord` can be
  re-evaluated to the **byte-identical** verdict and explanation, today or years from now.
- The optional `prev_hash` chain makes the audit log **tamper-evident**: any retroactive edit
  breaks the hash chain and is detectable.

> **The throughline:** *immutable, fully-pinned, canonically-serialized, coordination-free
> data.* Every future-proofing property above falls out of those four choices — which are the
> same choices that make the present-day engine deterministic, explainable, and auditable.
