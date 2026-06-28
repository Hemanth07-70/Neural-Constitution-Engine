# The Constitution Engine

> **Status:** Design document. This specifies the *intended* design of NCE's most important
> subsystem. No implementation exists yet. It builds on the system design in
> [`architecture.md`](architecture.md) and the principles in [`vision.md`](vision.md).
> Where this document and `architecture.md` differ in detail, this document is authoritative
> for the engine's semantics.

## Table of contents

1. [What is a Constitution?](#1-what-is-a-constitution)
2. [Constitutional Principles](#2-constitutional-principles)
3. [Constitution File Format](#3-constitution-file-format)
4. [Rule Types](#4-rule-types)
5. [Rule Evaluation Pipeline](#5-rule-evaluation-pipeline)
6. [Conflict Resolution](#6-conflict-resolution)
7. [Risk Levels](#7-risk-levels)
8. [Actions](#8-actions)
9. [Explainability](#9-explainability)
10. [Versioning](#10-versioning)
11. [Extensibility](#11-extensibility)
12. [Non-goals](#12-non-goals)

---

## 1. What is a Constitution?

A **Constitution** is a versioned, declarative document that defines the boundaries of
permitted behavior for an autonomous agent. It is the single source of truth the engine
consults to decide whether a proposed action may proceed, must be modified, requires a
human, or must be refused.

Precisely, a Constitution is:

> An ordered, versioned collection of **principles** and **rules**, together with the
> **metadata** and **resolution policy** required to evaluate any proposal deterministically
> and to explain the result.

A Constitution is **not** the agent, the model, or the prompt. It is an external artifact
the engine evaluates *against* a proposal. The agent proposes; the Constitution governs.

### Why constitutions are data, not code

NCE treats governance as **data** — declarative documents — rather than imperative logic
embedded in application code. This is a deliberate, load-bearing decision:

| Property | Consequence of data-as-governance |
| --- | --- |
| **Reviewable** | A constitution can be read, diffed, and approved by non-engineers — compliance, legal, security — the people who actually own the policy. |
| **Versionable** | Every change produces a new version with a full history; any past verdict can be tied to the exact rules in force at the time. |
| **Auditable** | The artifact that produced a decision is itself a stored record, not a transient code path. |
| **Portable** | The same constitution governs identically across runtimes, languages, and deployments. |
| **Testable** | Declarative rules over a typed proposal are exhaustively testable without executing arbitrary logic. |
| **Safe** | Data cannot perform I/O, recurse, or hang. A constitution cannot, by construction, contain a vulnerability of its own — only the engine that evaluates it can. |

Code expresses *how*; a constitution expresses *what is allowed*. Separating the two keeps
the policy legible to its owners and keeps the engine small, deterministic, and trustworthy.

> **Design tension, stated openly:** declarative rules are safer but less expressive than
> code. NCE resolves this through the **plugin model** (§11): when a rule genuinely needs
> custom logic, that logic lives in a vetted, versioned *evaluator* — never inline in the
> constitution. The constitution stays data; extensibility lives at a controlled boundary.

---

## 2. Constitutional Principles

A **principle** is a high-level, human-readable governing intent (e.g. *"Never disclose user
PII to third parties"*). Principles carry no executable matcher on their own; they are the
*why*. **Rules** (§3–4) are the machine-evaluable *how*, and each rule references the
principle(s) it serves. This linkage is what makes every verdict explainable in human terms.

Principles exist at five **scopes**, forming a hierarchy from broadest to narrowest:

| Scope | Owner | Purpose | Example |
| --- | --- | --- | --- |
| **Global** | NCE project / platform | Universal safety floor shipped with the engine. | "Never assist in creating weapons capable of mass casualties." |
| **Organization** | A deploying company | Company-wide policy, compliance, brand. | "All financial transactions over $10,000 require human approval." |
| **Project** | A team / application | Rules for one product or agent. | "This support agent may only access the tickets database." |
| **Session** | A single conversation/run | Temporary constraints for one execution context. | "During this incident, freeze all production writes." |
| **User** | The end user | Personal preferences, within the bounds above. | "Prefer concise answers; never email on my behalf without confirming." |

### Priority and inheritance

Scopes **inherit downward** (narrower scopes receive all principles from broader scopes) but
**cannot loosen** what a broader scope has restricted. This is the core invariant:

> **A narrower scope may further restrict, but never relax, a constraint imposed by a broader
> scope.**

Therefore the **restrictiveness precedence** (most authoritative first) is:

```
Global  >  Organization  >  Project  >  Session  >  User
```

- A **User** preference for verbose output is honored — unless a **Project** rule caps
  response length, in which case the cap wins.
- A **Session** "freeze production writes" rule can *add* a restriction the Organization did
  not impose, because adding restrictions is always permitted.
- A **User** rule can never *grant* access that the **Organization** denied. Attempts to do
  so are not errors — they are simply overridden, and the override is recorded in the
  explanation.

This asymmetry (restrictions compose upward in authority; permissions do not) is what makes
the hierarchy safe. It is enforced deterministically during conflict resolution (§6).

> The full set of principles and rules in force for a given proposal — the union across all
> five scopes, resolved into a single ordered rule set — is called the **effective
> constitution**. The engine always evaluates against the effective constitution, never a
> single scope in isolation.

---

## 3. Constitution File Format

Constitutions are authored in **YAML** for human readability, with a strict, validated
schema. The format is the public contract between policy authors and the engine.

### 3.1 Top-level schema

```yaml
# Constitution document — top-level structure
apiVersion: nce/v1                # Schema version of THIS file format (see §10)
kind: Constitution

metadata:
  id: org.acme.support-agent      # Stable, globally unique, immutable identifier
  version: 3.2.0                  # SemVer of the constitution's CONTENT (see §10)
  scope: project                  # global | organization | project | session | user
  title: "ACME Support Agent Constitution"
  description: "Governs the customer-support agent's permitted actions."
  author: "platform-team@acme.example"
  created_at: "2026-06-01T09:00:00Z"
  updated_at: "2026-06-28T14:30:00Z"
  status: published               # draft | published | deprecated | archived
  extends: org.acme.base          # Optional: inherit from a broader-scope constitution

# How conflicts are resolved for this document (see §6). Optional; defaults shown.
resolution:
  strategy: most-restrictive-wins
  default_verdict: block          # Fail-closed default when no rule matches confidently

principles:
  - id: P-PRIVACY
    statement: "Never disclose customer PII to unauthorized parties."
    category: privacy

rules:
  - id: R-001
    # ... see §3.2
```

### 3.2 Rule schema

```yaml
rules:
  - id: R-PII-EXPORT              # Stable, unique within the document
    title: "Block bulk PII export"
    description: >
      Prevents the agent from exporting more than a small number of customer
      records in a single action, which would constitute a data-exfiltration risk.
    principle: P-PRIVACY          # The principle this rule enforces (one or many)
    category: privacy             # See §4
    tags: [pii, exfiltration, gdpr]
    severity: high                # informational | low | medium | high | critical (§7)
    enabled: true

    # WHEN does this rule apply? A declarative condition over the proposal.
    condition:
      all:                        # all | any | not — composable boolean groups
        - field: action.type
          op: equals
          value: data.export
        - field: action.params.record_count
          op: greater_than
          value: 25

    # WHAT happens when the condition matches? (see §8)
    action:
      type: block
      message: "Bulk PII export exceeds the permitted threshold of 25 records."

    # Optional metadata aiding triage and review
    references:
      - "ACME Data Handling Policy §4.2"
      - "GDPR Art. 5(1)(c) — data minimisation"
```

#### Condition operators (the matcher vocabulary)

Conditions are pure, side-effect-free predicates over the normalized proposal. The core
engine ships a fixed, well-tested operator set; richer matching is delegated to evaluator
plugins (§11) rather than expanding this vocabulary uncontrollably.

| Operator | Meaning |
| --- | --- |
| `equals` / `not_equals` | Scalar equality |
| `in` / `not_in` | Membership in a list |
| `greater_than` / `less_than` / `gte` / `lte` | Numeric / temporal comparison |
| `matches` | Regular-expression match against a string field |
| `contains` | Substring or collection membership |
| `exists` / `absent` | Presence of a field |
| `evaluator` | Delegate to a named plugin evaluator (§11) |

Boolean groups `all` / `any` / `not` compose operators into arbitrary trees.

### 3.3 Realistic examples

**Example A — Organization: high-value transactions need a human.**

```yaml
- id: R-FIN-APPROVAL
  title: "Human approval for large transactions"
  description: "Any money movement at or above $10,000 must be approved by a human."
  principle: P-FINANCIAL-CONTROL
  category: compliance
  tags: [finance, sox, approval]
  severity: high
  condition:
    all:
      - field: action.type
        op: in
        value: [payment.send, transfer.create, refund.issue]
      - field: action.params.amount_usd
        op: gte
        value: 10000
  action:
    type: request_human_approval
    message: "Transactions of $10,000 or more require approval from a finance approver."
    approver_role: finance-approver
```

**Example B — Safety: refuse dangerous operational commands.**

```yaml
- id: R-OPS-NO-PROD-DROP
  title: "Never drop production databases"
  principle: P-OPERATIONAL-SAFETY
  category: safety
  tags: [database, destructive, production]
  severity: critical
  condition:
    all:
      - field: action.type
        op: equals
        value: db.execute
      - field: action.params.statement
        op: matches
        value: "(?i)\\b(drop|truncate)\\b"
      - field: context.environment
        op: equals
        value: production
  action:
    type: block
    message: "Destructive DDL is not permitted against production databases."
```

**Example C — Privacy: redact rather than refuse (a `rewrite` action).**

```yaml
- id: R-PII-REDACT
  title: "Redact PII in outbound messages"
  principle: P-PRIVACY
  category: privacy
  tags: [pii, redaction]
  severity: medium
  condition:
    all:
      - field: action.type
        op: equals
        value: message.send
      - field: action.params.body
        op: evaluator
        value: pii-detector            # plugin evaluator (§11)
  action:
    type: rewrite
    transform: redact-pii              # named, vetted transform
    message: "Detected PII was redacted before sending."
```

**Example D — User preference: style, honored only when nothing stricter applies.**

```yaml
- id: R-USER-CONCISE
  title: "Prefer concise responses"
  principle: P-USER-PREFERENCE
  category: operational
  severity: informational
  condition:
    field: action.type
    op: equals
    value: message.send
  action:
    type: warn
    message: "User prefers concise responses; consider shortening."
```

---

## 4. Rule Types

Rules are organized into **categories**. Categories are a *taxonomy for humans* (filtering,
reporting, ownership) and a *default-severity hint*; they do not change evaluation
mechanics — every category flows through the same pipeline. This keeps the engine uniform
while keeping constitutions navigable.

| Category | Governs | Typical severity | Example intent |
| --- | --- | --- | --- |
| **safety** | Prevention of physical, systemic, or irreversible harm. | high–critical | No destructive production commands; no unsafe instructions. |
| **privacy** | Handling of personal and confidential data. | medium–high | No PII disclosure; redaction; data minimisation. |
| **security** | Protection against misuse, escalation, exfiltration. | high–critical | No credential exposure; no privilege escalation. |
| **compliance** | Adherence to law, regulation, contracts. | high | SOX approvals; GDPR; data-residency. |
| **ethical** | Fairness, honesty, dignity, non-deception. | medium–high | No deceptive messaging; no discriminatory actions. |
| **operational** | Correct, reliable system operation. | low–medium | Change windows; rate limits; environment guards. |
| **cost** | Financial guardrails on resource consumption. | low–medium | Cap spend per action/session; require approval over budget. |
| **performance** | Latency, throughput, resource efficiency. | informational–medium | Limit batch sizes; prevent expensive scans. |
| **organization-specific** | Bespoke policy unique to a deployer. | varies | Brand voice; partner-specific restrictions. |

> **Extensibility note:** the category set is open. Deployers may declare custom categories
> in the `organization-specific` family. The engine treats unknown categories as opaque
> labels — they participate in filtering and reporting but never alter evaluation order,
> which is governed solely by severity and scope (§6). This guarantees that adding a category
> can never change an existing verdict.

---

## 5. Rule Evaluation Pipeline

Every proposal flows through a single, **deterministic, ordered** pipeline. Determinism is
non-negotiable: *the same proposal against the same effective constitution must always
produce the same verdict and the same explanation.* No stage performs hidden I/O, and no
stage depends on wall-clock time or randomness except where a value is explicitly supplied
on the proposal (e.g. `context.timestamp`).

### 5.1 Stages

| # | Stage | Responsibility | Failure behavior |
| --- | --- | --- | --- |
| 1 | **Ingest & authenticate** | Verify caller identity; accept the raw proposal. | Reject → audited `block`. |
| 2 | **Validate** | Check the proposal against the proposal schema. | Invalid → `block` (fail-closed). |
| 3 | **Resolve constitution** | Assemble the *effective constitution* (union across scopes, per §2) at a pinned version. | Cannot resolve → `block`. |
| 4 | **Normalize** | Canonicalize the proposal (field order, types, units) so matching and audit records are stable. | Error → `block`. |
| 5 | **Match** | Evaluate each enabled rule's `condition` against the normalized proposal. Collect all matches. | Evaluator error → that rule yields a `block`-leaning match, audited. |
| 6 | **Resolve conflicts** | Apply deterministic precedence (§6) to the set of matched rules → one winning action. | Tie → deterministic tiebreak (§6). |
| 7 | **Decide** | Produce the final verdict and (for `rewrite`) the transformed proposal. | — |
| 8 | **Justify** | Build the structured explanation (§9): winning rule, contenders, reasoning. | — |
| 9 | **Record** | Append the immutable audit entry *before* returning the verdict. | Write failure → `block` (never return an unrecorded allow). |

A key ordering guarantee: **the audit record is written before the verdict is returned.** An
action is never permitted without first being recorded.

### 5.2 Sequence diagram

```
 Agent            API Layer        Engine Pipeline                 Stores
   │                  │                  │                            │
   │   proposal       │                  │                            │
   ├─────────────────▶│                  │                            │
   │                  │  authenticate    │                            │
   │                  ├─────────────────▶│ (1) ingest & auth          │
   │                  │                  │ (2) validate schema         │
   │                  │                  │ (3) resolve effective       │
   │                  │                  │     constitution  ─────────▶│ Constitution
   │                  │                  │                  ◀───────────│   Store
   │                  │                  │ (4) normalize proposal      │
   │                  │                  │ (5) match all rules         │
   │                  │                  │      └─ evaluator plugin?    │
   │                  │                  │         (sandboxed, §11)     │
   │                  │                  │ (6) resolve conflicts        │
   │                  │                  │ (7) decide verdict           │
   │                  │                  │ (8) build explanation        │
   │                  │                  │ (9) APPEND audit  ──────────▶│ Audit Trail
   │                  │                  │                  ◀───────────│ (ack)
   │                  │   verdict +      │                            │
   │   verdict +      │   explanation    │                            │
   │   explanation    │◀─────────────────┤                            │
   │◀─────────────────┤                  │                            │
   │                  │                  │                            │
```

For a `request_human_approval` verdict, the agent's call resolves to a *pending* state; the
proposal is parked, a human is notified, and the eventual human decision is itself recorded
as a linked audit entry. The engine remains stateless about the human's deliberation — it
only records the request and the outcome.

---

## 6. Conflict Resolution

When multiple rules match a single proposal, the engine must select exactly one **winning
action**, deterministically. The resolution algorithm applies the following ordered criteria;
each criterion is a tiebreaker for the one above it.

1. **Action authority.** The most restrictive action wins. The total order of actions, from
   most to least restrictive, is:

   ```
   block  >  escalate  >  request_human_approval  >  rewrite  >  warn  >  allow
   ```

   A `block` from any matched rule defeats every less-restrictive action. This is the
   operational expression of **fail-closed**.

2. **Scope authority.** Among rules proposing the *same* action, the broader scope wins,
   per the hierarchy in §2:

   ```
   Global  >  Organization  >  Project  >  Session  >  User
   ```

   This enforces the invariant that a narrower scope can restrict but never relax.

3. **Severity.** Among rules of equal action and equal scope, higher severity wins:

   ```
   critical  >  high  >  medium  >  low  >  informational
   ```

4. **Explicit priority.** If still tied, an optional integer `priority` field on the rule
   breaks the tie (higher wins). Absent on both, treated as `0`.

5. **Lexical rule id.** As a final, total tiebreaker, the rule whose `id` sorts first
   lexicographically wins. This guarantees a deterministic outcome in *all* cases — there is
   never an unresolved tie.

> **Worked example.** A proposal matches three rules: a User `allow`, a Project
> `request_human_approval`, and an Organization `block`. Criterion 1 (action authority)
> selects the `block` immediately — scope and severity are never consulted. The other two
> rules are recorded in the explanation as *overridden contenders* (§9), so the author can
> see exactly why the permissive rules did not win.

**Non-blocking actions still apply.** Resolution picks one *winning* action, but advisory
outcomes are not discarded: every matched `warn` is attached to the explanation, and a
`rewrite` whose transform does not conflict with the winning action may be composed in
(e.g. redact-then-approve). Composition rules are themselves deterministic and documented per
transform; when in doubt, the more restrictive winning action suppresses composition.

---

## 7. Risk Levels

Every rule carries a **severity**; every verdict carries a derived **risk level** (the
severity of the winning rule, or the highest severity among contributing rules for composite
outcomes). Risk levels are the bridge between *policy* and *operational consequence*.

| Level | Meaning | Effect on execution |
| --- | --- | --- |
| **informational** | Advisory only; no governance concern. | Action proceeds; note recorded for visibility. |
| **low** | Minor concern; acceptable with awareness. | Proceeds; `warn` surfaced to caller; audited. |
| **medium** | Notable concern; should be corrected. | May `warn` or `rewrite`; proceeds in modified form; audited prominently. |
| **high** | Serious concern; must not proceed unchecked. | Typically `request_human_approval` or `block`; never silently allowed. |
| **critical** | Severe / irreversible harm potential. | `block` (and may `escalate`); proceeds only via an explicit, audited human override where policy permits one. |

Risk level is **descriptive of policy**, while the **action** is **prescriptive of
behavior**. They are correlated by convention (the default-severity hints in §4) but
independent in mechanism: an author may attach any action to any severity. The engine reports
both, so reviewers can detect mismatches (e.g. a `critical` rule wired only to `warn`) during
constitution review — a deliberate safeguard against misconfiguration rather than a silent
correction.

---

## 8. Actions

An **action** is the prescribed outcome when a rule matches. NCE defines a fixed, closed set
of six action types — closed by design, because the set of things the engine can *do* to a
proposal must be small, well-understood, and exhaustively testable. (These six refine the
coarse `allow`/`deny`/`modify` verdicts described in `architecture.md`: `allow`→`allow`,
`deny`→`block`, `modify`→`rewrite`, with `warn`, `request_human_approval`, and `escalate`
added as governance-specific outcomes.)

| Action | Effect | Returns to agent | When to use |
| --- | --- | --- | --- |
| **allow** | Proposal proceeds unchanged. | Approved proposal. | No concern, or explicitly permitted. |
| **warn** | Proceeds, but a warning is attached. | Approved proposal + warning(s). | Low-risk concerns; visibility without obstruction. |
| **rewrite** | Proposal is transformed by a named, vetted transform, then proceeds. | Modified proposal + note. | Salvageable actions (e.g. redact PII, cap a batch size). |
| **request_human_approval** | Proposal is parked pending a human decision. | Pending; resolves on human action. | Consequential but legitimate actions needing oversight. |
| **block** | Proposal is refused. | Denial + reason. | Disallowed actions; the fail-closed default. |
| **escalate** | Refused *and* routed to a designated responder/alert. | Denial + escalation ack. | Critical violations, suspected misuse, security events. |

Design constraints on actions:

- **Transforms are named and vetted, never inline.** A `rewrite` references a registered
  transform (e.g. `redact-pii`) — a constitution can request a transform but cannot define
  arbitrary transformation logic. This keeps constitutions pure data (§1) and keeps all
  executable behavior inside the auditable engine/plugin boundary (§11).
- **Every action is auditable and reversible in record.** Even `allow` produces a record; a
  `rewrite` records both the original and transformed proposal.
- **`escalate` is `block` plus a side effect.** It never lets an action through; the
  escalation is an additional, separately recorded event.

---

## 9. Explainability

Every verdict — without exception, including `allow` — produces a **structured explanation**.
A governance decision that cannot be explained is not acceptable (see `vision.md`). The
explanation is machine-readable (for dashboards, alerts, and downstream tooling) and renders
cleanly for humans. The structure below is illustrated in YAML for readability; it is a data
contract, not code.

```yaml
explanation:
  decision_id: 9f1c2a7e-...          # Unique, links to the audit record
  timestamp: "2026-06-28T14:31:02Z"  # From the proposal context, not wall-clock
  verdict:
    action: block                    # The resolved action (§8)
    risk_level: critical             # The derived risk level (§7)
  proposal_summary:
    actor: agent://acme/support-bot
    action_type: db.execute
    target: production.customers

  # The rule that determined the outcome
  determining_rule:
    id: R-OPS-NO-PROD-DROP
    title: "Never drop production databases"
    scope: organization
    category: safety
    severity: critical
    principle: P-OPERATIONAL-SAFETY
    statement: "Production data must never be destroyed by an autonomous action."
    message: "Destructive DDL is not permitted against production databases."

  # Why this rule won over the others (traces §6)
  resolution:
    strategy: most-restrictive-wins
    decided_by: action-authority      # which criterion settled it
    overridden_contenders:            # matched but did not win
      - { id: R-USER-CONCISE, scope: user, action: warn, reason: "lower authority" }

  # Non-winning advisory outputs that still apply
  warnings: []
  applied_transforms: []

  references:
    - "ACME Data Handling Policy §4.2"

  # Full provenance for reproducibility
  context:
    constitution_id: org.acme.support-agent
    constitution_version: 3.2.0
    engine_version: 0.1.0
    evaluator_plugins: []             # name@version of any plugins consulted
```

Required guarantees of the explanation:

- **Traceable** — names the determining rule, its principle, and the human-readable
  statement of intent.
- **Complete** — lists overridden contenders and *why* they lost (which precedence criterion
  decided it), so authors can debug policy, not guess.
- **Reproducible** — pins the constitution version, engine version, and plugin versions, so
  the exact decision can be replayed.
- **Stable** — identical inputs yield byte-identical explanations (determinism, §5).

---

## 10. Versioning

Three independent version axes evolve at different rates and must not be conflated:

| Axis | Field | Governs | Cadence |
| --- | --- | --- | --- |
| **Schema (format) version** | `apiVersion` | The structure of the constitution file itself. | Rare; engine-driven. |
| **Constitution (content) version** | `metadata.version` | The principles and rules of one document. | Frequent; author-driven. |
| **Engine version** | runtime | The evaluator implementation. | Independent of both above. |

### 10.1 Constitution content versioning (SemVer)

`metadata.version` follows [Semantic Versioning](https://semver.org/):

- **MAJOR** — a change that can make a previously-allowed proposal now blocked (or otherwise
  alters verdicts in a backward-incompatible way): tightening a rule, removing a permission.
- **MINOR** — additive, backward-compatible: new advisory rules, new tags, expanded
  documentation that cannot flip an existing allow to a block in a surprising way.
- **PATCH** — clarifications with no behavioral effect: wording, references, metadata.

> Because tightening policy is the *expected and desirable* direction for a governance tool,
> a MAJOR bump is normal and not alarming — it is simply the honest signal that some
> previously-permitted behavior is now restricted. Authors are expected to bump MAJOR
> liberally rather than disguise tightening as MINOR.

### 10.2 Immutability and lifecycle

- A **published** version is **immutable**. New behavior means a new version, never an edit
  in place. This is what lets any audit record name the *exact* rules that produced it.
- Lifecycle: `draft → published → deprecated → archived`. Deprecated versions still evaluate
  (for replay and gradual migration) but warn on new adoption; archived versions are retained
  for audit but are no longer selectable for live evaluation.

### 10.3 Backward compatibility

- **Pinning.** A deployment pins a constitution version; the engine never silently upgrades
  the policy governing a running agent.
- **Replay.** Any historical proposal can be re-evaluated against its original
  constitution + engine version, reproducing the original verdict exactly (§9
  reproducibility).
- **Schema migration.** When `apiVersion` advances, the engine ships a migration that
  transforms older documents to the new schema; old `apiVersion`s remain readable for a
  documented support window. The engine refuses (fail-closed) to evaluate a schema version it
  does not understand rather than guessing.

---

## 11. Extensibility

The core engine deliberately understands only a small, fixed condition vocabulary (§3.2) and
a closed action set (§8). Real deployments will need richer matching — a PII detector, a
toxicity classifier, a cost estimator, a domain-specific risk model. These are added through
a **plugin model** so that *new capabilities never require modifying the core engine.*

### 11.1 The evaluator plugin contract

A plugin is a **named, versioned evaluator** invoked from a rule's `condition` via the
`evaluator` operator (§3.2). Conceptually it is a pure function:

> *Given a normalized proposal and declared parameters, return a deterministic boolean (does
> this rule match?) and an optional structured finding for the explanation.*

The contract is intentionally narrow:

| Requirement | Rationale |
| --- | --- |
| **Pure & deterministic** | Same input → same output. Preserves the engine's core guarantee (§5). |
| **Side-effect free** | An evaluator may not perform external I/O on the hot path; any model or data it needs is provided through a declared, injected interface. Keeps evaluation reproducible and sandboxable. |
| **Versioned** | Referenced as `name@version`; the version is pinned and recorded in every explanation (§9). |
| **Declared & registered** | Plugins are registered with the engine out-of-band and allow-listed per constitution. A constitution cannot summon arbitrary code. |
| **Sandboxed & bounded** | Executed under time/resource limits; a failing or timed-out evaluator yields a fail-closed (`block`-leaning) match, audited. |

### 11.2 Two extension surfaces

1. **Condition evaluators** — answer "does this rule apply?" for matching that exceeds the
   built-in operators (classifiers, detectors, scorers).
2. **Transforms** — implement `rewrite` actions (e.g. `redact-pii`, `cap-batch-size`). Also
   named, versioned, registered, and recorded.

Both surfaces are *additive*: registering a new evaluator or transform changes behavior only
for constitutions that explicitly reference it. Existing verdicts are unaffected — the same
guarantee that protects category extensibility (§4).

### 11.3 What the plugin model deliberately forbids

- Plugins cannot add new **action types** — the action set is closed (§8).
- Plugins cannot alter **conflict-resolution precedence** (§6) — resolution is core and
  fixed.
- Plugins cannot mutate the **audit trail** or the **explanation contract** — only contribute
  findings to it.

This keeps the *trusted computing base* — the parts that must be correct for governance to be
trustworthy — small and stable, while allowing the *matching intelligence* to grow without
bound.

---

## 12. Non-goals

To stay small, deterministic, and trustworthy, the Constitution Engine explicitly does **not**
take responsibility for the following. Each is owned elsewhere in the system or outside NCE
entirely.

| The engine is **not** responsible for… | …because |
| --- | --- |
| **Generating, training, or hosting models.** | NCE governs *actions*, not cognition. |
| **Planning or orchestrating agent behavior.** | The agent decides *what to propose*; the engine only judges proposals. |
| **Authoring constitutions for the deployer.** | Policy ownership stays with the organization; NCE provides the format and the evaluator, not the rules. |
| **Enforcing verdicts in the outside world.** | The engine *decides and records*; the calling integration is responsible for honoring a `block` or executing an `allow`. (NCE's value depends on callers being unable to bypass it — an integration concern, not an engine concern.) |
| **Judging the correctness of a model's reasoning.** | It governs the *action proposed*, not the *thoughts behind it*. |
| **Being the human in the loop.** | For `request_human_approval`/`escalate`, the engine routes and records; it does not substitute its judgment for the human's. |
| **Long-term identity, RBAC, or secrets management.** | Caller identity is *consumed* by the engine but *owned* by the surrounding platform. |
| **Guaranteeing a constitution is wise or complete.** | The engine guarantees *faithful, deterministic, explainable enforcement* of whatever policy it is given — not that the policy itself is good. Garbage in, faithfully-and-traceably-enforced garbage out. |

> The discipline of these non-goals is what lets the engine make its core promises:
> **deterministic, explainable, fail-closed enforcement of declarative policy.** Everything
> outside that promise is, by design, someone else's job.

---

## Summary of guarantees

The Constitution Engine commits to five properties that all other design choices serve:

1. **Deterministic** — identical inputs always yield identical verdicts and explanations.
2. **Fail-closed** — uncertainty, error, or absence of a matching rule defaults to `block`.
3. **Explainable** — every decision, including `allow`, emits a complete structured rationale.
4. **Auditable** — every decision is recorded immutably *before* it takes effect.
5. **Extensible without compromise** — new matching intelligence is added at a controlled
   plugin boundary that cannot weaken the four guarantees above.
