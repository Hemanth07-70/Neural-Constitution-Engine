# Backend — Governance Service (reserved)

> **Status: not yet implemented.** This directory is reserved for the NCE governance
> service. No FastAPI application, dependencies, or business logic exist yet. Implementation
> begins in **M1 / M2** (see [`../docs/roadmap.md`](../docs/roadmap.md)).

The backend will host the deterministic evaluation engine and expose it over a stable
FastAPI interface. Its design — including the layered structure and the rule that the pure
core (`engine/`, `domain/`) must never depend on the web framework — is specified in
[`../docs/architecture.md`](../docs/architecture.md#recommended-backend-structure-fastapi--not-yet-implemented).

## Planned layout

```
backend/
├── app/
│   ├── main.py                # FastAPI application entrypoint
│   ├── api/                   # Transport layer (routers, dependencies, schemas)
│   ├── core/                  # Config, logging, security
│   ├── domain/                # Pure domain model
│   ├── engine/                # Deterministic evaluation pipeline (framework-free)
│   ├── services/              # Orchestration
│   ├── repositories/          # Persistence interfaces and implementations
│   └── schemas/               # Pydantic request/response models
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── Dockerfile
```

When implementation starts, this README will be replaced with setup, run, and test
instructions.
