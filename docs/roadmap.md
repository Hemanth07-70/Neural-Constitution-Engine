# Roadmap

This roadmap describes the planned evolution of NCE from foundations to a stable 1.0. It is
a living document; milestones and ordering may shift as the design matures. Versions follow
[Semantic Versioning](https://semver.org/).

> **Current milestone:** **M0 — Foundations** (in progress).

## M0 — Foundations · `pre-alpha`

Establish the project so long-term development can proceed with discipline.

- [x] Repository initialization and project structure
- [x] Licensing (MIT) and governance documents
- [x] Vision, architecture, and roadmap documentation
- [x] Tooling conventions (`.gitignore`, `.editorconfig`)
- [x] Reserved `backend/` and `frontend/` directories with documented layouts
- [ ] Contribution and RFC process finalized
- [ ] Continuous integration scaffolding

## M1 — The Engine Core · `0.1.0`

Implement the deterministic heart of the system, framework-free.

- [ ] Domain model: `Constitution`, `Principle`, `Rule`, `Proposal`, `Verdict`
- [ ] Evaluation pipeline (ingest → normalize → match → resolve → decide → justify)
- [ ] Conflict-resolution precedence and the fail-closed guarantee
- [ ] Exhaustive unit tests for the engine
- [ ] Constitution schema and validation

## M2 — Governance Service · `0.2.0`

Expose the engine over a stable API.

- [ ] FastAPI service wrapping the engine
- [ ] Endpoints: submit proposal, manage constitutions, query audits
- [ ] Authentication and authorization
- [ ] Persistent constitution store with versioning, diffing, and rollback
- [ ] Append-only, tamper-evident audit trail
- [ ] Integration test suite and containerization

## M3 — Dashboard · `0.3.0`

Give humans a first-class interface.

- [ ] Next.js dashboard (App Router)
- [ ] Constitution authoring and version management
- [ ] Proposal simulation against draft constitutions
- [ ] Audit trail explorer with filtering and export

## M4 — Integration & SDKs · `0.4.0`

Make NCE easy to adopt from any agent runtime.

- [ ] Official client SDK(s)
- [ ] Reference integrations with popular agent frameworks
- [ ] Example projects and end-to-end tutorials

## M5 — Hardening · `0.5.0`

Prepare for production use.

- [ ] Performance benchmarking and optimization of the hot path
- [ ] Observability: metrics, structured logging, tracing
- [ ] Security review and threat modeling
- [ ] Operational documentation (deployment, scaling, backup/restore)

## 1.0 — Stable Release

- [ ] API stability commitment and deprecation policy
- [ ] Comprehensive documentation and migration guides
- [ ] Production case studies
- [ ] Long-term support plan

## How to influence the roadmap

The roadmap is shaped in the open. Open an issue to propose changes, or submit an RFC for
significant additions (see [`CONTRIBUTING.md`](../CONTRIBUTING.md)).
