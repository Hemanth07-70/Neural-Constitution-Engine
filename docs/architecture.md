# Architecture

> **Status:** Design document. This describes the *intended* system. No application code
> has been implemented yet. Folder structures below are recommendations to be realized
> across upcoming milestones (see [`roadmap.md`](roadmap.md)).

## System overview

NCE is composed of a **governance service** (the engine, exposed over an API) and a
**dashboard** (for authoring constitutions and reviewing audits). Agents interact with the
service; humans interact with the dashboard.

```
                          ┌───────────────────────────────────────────────┐
                          │            Neural Constitution Engine           │
   ┌──────────┐ proposal  │  ┌──────────┐  ┌───────────────┐  ┌──────────┐ │
   │   Agent   │ ───────▶ │  │  API     │─▶│  Evaluation   │─▶│  Verdict │ │
   │ (any RT)  │          │  │  Layer   │  │  Pipeline     │  │  Builder │ │
   │           │ ◀─────── │  └──────────┘  └───────┬───────┘  └────┬─────┘ │
   └──────────┘  verdict  │                        │               │       │
                          │              ┌─────────▼──────┐  ┌──────▼─────┐ │
                          │              │ Constitution   │  │  Audit     │ │
                          │              │ Store          │  │  Trail     │ │
                          │              └────────────────┘  └──────┬─────┘ │
                          └─────────────────────────────────────────┼──────┘
                                                                     │
                                                            ┌────────▼────────┐
                                                            │   Dashboard     │
                                                            │   (Next.js)     │
                                                            └─────────────────┘
```

## Core domain model

| Entity | Responsibility |
| --- | --- |
| **Constitution** | A versioned, immutable-once-published collection of principles and rules with metadata (id, version, status, effective date). |
| **Principle** | A human-readable governing intent. Carries no executable logic on its own. |
| **Rule** | A machine-evaluable predicate referencing one or more principles. Has a type (e.g. `allow`, `deny`, `require_approval`, `transform`) and a matcher over proposal attributes. |
| **Proposal** | The action an agent intends to take: actor identity, action type, target, parameters, and context. |
| **Verdict** | The outcome: `allow` \| `deny` \| `modify`, plus the rules that fired and a human-readable justification. |
| **Audit Record** | An append-only entry capturing the proposal, the active constitution version, the verdict, the justification, and a timestamp. |

## The evaluation pipeline

Every proposal flows through a deterministic, ordered pipeline. Determinism is essential:
the same proposal against the same constitution version must always yield the same verdict.

1. **Ingest & validate** — Authenticate the caller, validate the proposal schema, and
   resolve the active constitution version.
2. **Normalize** — Canonicalize the proposal (consistent field ordering, types) so matching
   is reliable and audit records are comparable.
3. **Match** — Determine which rules apply to this proposal.
4. **Resolve** — Apply conflict-resolution precedence (e.g. explicit deny overrides allow;
   more-specific rules override broader ones). The resolution strategy is itself part of the
   constitution metadata.
5. **Decide** — Produce a verdict. `modify` verdicts include the transformed proposal.
6. **Justify** — Attach the human-readable reasoning and the list of rules that fired.
7. **Record** — Write the immutable audit entry before the verdict is returned to the caller.

**Fail-closed guarantee:** if any stage errors or the engine cannot reach a confident
decision, the default verdict is `deny`, and the failure itself is audited.

## Components

### API layer (FastAPI)
The synchronous control surface. Exposes endpoints for submitting proposals, managing
constitutions, and querying audit records. Responsible for authentication, request
validation, and translating between transport and the domain model. Kept thin — it
delegates all decision logic to the evaluation pipeline.

### Evaluation pipeline
The heart of the system and the only place verdicts are produced. Pure and deterministic by
design, so it is straightforward to test exhaustively and to reason about.

### Constitution store
Persists constitutions and their version history. Published versions are immutable; new
behavior means a new version. Supports diffing and rollback.

### Audit trail
Append-only, tamper-evident store of every decision. Designed to be queryable for compliance
("show all denied money-movement proposals last quarter") and forensics ("explain this
specific action").

### Dashboard (Next.js)
The human interface: author and review constitutions, simulate proposals against a draft
constitution before publishing, and explore the audit trail.

## Recommended backend structure (FastAPI) — not yet implemented

A clean, layered structure that keeps the API thin and the domain logic pure:

```
backend/
├── app/
│   ├── main.py                # FastAPI application entrypoint
│   ├── api/                   # Transport layer (routers, dependencies, schemas)
│   │   ├── routes/            # Endpoint definitions grouped by resource
│   │   └── dependencies.py    # Shared request dependencies (auth, pagination)
│   ├── core/                  # Cross-cutting concerns: config, logging, security
│   ├── domain/                # Pure domain model: Constitution, Rule, Proposal, Verdict
│   ├── engine/                # The evaluation pipeline (the heart — framework-free)
│   ├── services/              # Orchestration between API, engine, and stores
│   ├── repositories/          # Persistence interfaces and implementations
│   └── schemas/               # Pydantic request/response models
├── tests/
│   ├── unit/                  # Domain and engine tests (no I/O)
│   └── integration/           # API and persistence tests
├── pyproject.toml             # Dependencies and tooling config
└── Dockerfile
```

Guiding rule: **`engine/` and `domain/` must not import from `api/`.** Dependencies point
inward toward the pure core, never outward toward the framework.

## Recommended frontend structure (Next.js) — not yet implemented

App Router based, feature-oriented:

```
frontend/
├── app/                       # Next.js App Router (routes, layouts)
│   ├── constitutions/         # Authoring and version management views
│   ├── audit/                 # Audit trail explorer
│   └── layout.tsx
├── components/                # Reusable presentational components
├── features/                  # Feature modules (state + UI for a domain area)
├── lib/                       # API client, formatting, shared utilities
├── hooks/                     # Reusable React hooks
├── types/                     # Shared TypeScript types (mirroring the API contract)
├── public/                    # Static assets
├── package.json
└── Dockerfile
```

Guiding rule: the API contract (`types/`) is the single source of truth shared between
features; components stay presentational and receive data via features/hooks.

## Cross-cutting concerns

- **Authentication & authorization** — Callers (agents and humans) are authenticated;
  constitution editing is privileged and itself audited.
- **Observability** — Structured logs, metrics on verdict latency and allow/deny rates, and
  tracing through the pipeline.
- **Versioning** — Both the API and constitutions are explicitly versioned; verdicts always
  record which constitution version produced them.
- **Deployment** — Backend and frontend are containerized (see the reserved `Dockerfile`s)
  for reproducible, portable deployment.

## Key design decisions (and why)

| Decision | Rationale |
| --- | --- |
| Engine is pure and deterministic | Exhaustive testability; reproducible verdicts; trustworthy audits. |
| Constitutions are versioned and immutable once published | A verdict can always be tied to the exact rules in force at the time. |
| Fail closed by default | A governance layer that fails open is worse than no governance layer. |
| Thin API over a framework-free core | The engine outlives any web framework choice and is reusable beyond HTTP. |
| Separate dashboard service | Human authoring/review concerns evolve independently from the hot path. |
