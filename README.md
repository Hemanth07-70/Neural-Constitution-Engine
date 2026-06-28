<div align="center">

# Neural Constitution Engine (NCE)

**A production-grade governance framework for autonomous AI agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Pre-Alpha](https://img.shields.io/badge/status-pre--alpha-orange.svg)](docs/roadmap.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

> ⚠️ **Project status: pre-alpha (M0 — Foundations).**
> NCE is in the design and scaffolding phase. There is no installable package yet.
> This repository currently contains the project's vision, architecture, and governance
> documents. Follow the [roadmap](docs/roadmap.md) to track progress.

## What is NCE?

The **Neural Constitution Engine** is a governance layer that sits between an autonomous
agent and the actions it wants to take in the world. Agents *propose* actions; NCE
*evaluates* each proposal against a declarative **constitution** — a versioned set of
principles and rules — and returns a verdict: **allow**, **deny**, or **modify**. Every
decision is recorded in an immutable, queryable **audit trail**.

In short: NCE is the difference between an agent that *can* act and an agent that is
*permitted* to act, with a complete record of why.

## Why does it exist?

Autonomous agents increasingly take consequential actions — sending emails, moving money,
modifying infrastructure, writing to production systems. The prompt that shapes their
behavior is not an enforcement boundary; it is a suggestion. Organizations deploying these
agents need a layer that is:

- **Declarative** — governance expressed as data (constitutions), not buried in code.
- **Auditable** — every decision explained and recorded for compliance and forensics.
- **Independent** — enforced outside the model, so a jailbroken or confused agent cannot
  bypass it.
- **Composable** — usable from any agent runtime via a clean API and SDKs.

NCE aims to be to AI governance what a policy engine (e.g. OPA) is to infrastructure
authorization: a focused, well-understood, production-ready primitive.

## Core concepts

| Concept | Description |
| --- | --- |
| **Constitution** | A versioned document of principles and rules that define permitted agent behavior. |
| **Principle** | A high-level, human-readable governing intent (e.g. "Never disclose user PII to third parties"). |
| **Rule** | A concrete, machine-evaluable predicate derived from one or more principles. |
| **Proposal** | An action an agent intends to take, submitted to the engine for evaluation. |
| **Verdict** | The engine's decision: `allow`, `deny`, or `modify`, with a justification. |
| **Audit Record** | An immutable log entry capturing the proposal, verdict, and reasoning. |

See [`docs/vision.md`](docs/vision.md) for the philosophy and [`docs/architecture.md`](docs/architecture.md)
for how these fit together.

## Architecture at a glance

```
        ┌──────────────┐   proposal    ┌─────────────────────────────┐
        │  AI Agent    │ ────────────▶ │   Neural Constitution Engine │
        │  (any runtime)│              │  ┌────────────────────────┐ │
        │              │ ◀──────────── │  │  Evaluation Pipeline   │ │
        └──────────────┘    verdict    │  └────────────────────────┘ │
                                       │   Constitution Store         │
                                       │   Audit Trail                │
                                       └──────────────┬──────────────┘
                                                      │
                                              ┌───────▼────────┐
                                              │  Dashboard     │
                                              │  (Next.js)     │
                                              └────────────────┘
```

The engine is exposed as a **FastAPI** service. A **Next.js** dashboard provides authoring
of constitutions and review of audit logs. Full design in
[`docs/architecture.md`](docs/architecture.md).

## Repository layout

```
neural-constitution-engine/
├── docs/            # Vision, architecture, and roadmap
├── backend/         # FastAPI governance service (reserved — not yet implemented)
├── frontend/        # Next.js dashboard        (reserved — not yet implemented)
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── CHANGELOG.md
```

## Getting involved

NCE is being built in the open and welcomes contributors. The best place to start:

1. Read the [vision](docs/vision.md) and [architecture](docs/architecture.md).
2. Review the [roadmap](docs/roadmap.md) to see what's planned.
3. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) — significant changes begin as design proposals.

## License

NCE is released under the [MIT License](LICENSE).
