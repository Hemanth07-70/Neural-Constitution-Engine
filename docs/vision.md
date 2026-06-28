# Vision

## The problem

Autonomous AI agents are moving from demos to production. They send communications, execute
transactions, modify infrastructure, and write to systems of record. The mechanism most
teams rely on to constrain this behavior is the prompt — a set of natural-language
instructions embedded in the model's context.

A prompt is not a control. It is a *request*. It can be overridden by adversarial input,
eroded by long conversations, misinterpreted by the model, or simply ignored under
distribution shift. Relying on the same system that *takes* actions to also *police* those
actions is a conflict of interest with no enforcement boundary.

What is missing is an **independent, declarative, auditable** layer that decides what an
agent is permitted to do — separate from the model, expressed as data, and accountable
after the fact.

## What NCE is

The Neural Constitution Engine is that layer. It sits between an agent and its effects on
the world and answers one question for every action an agent proposes:

> *Given the active constitution, is this action permitted — and if so, in what form?*

It returns one of three verdicts — **allow**, **deny**, or **modify** — together with a
justification, and it records every decision in an immutable audit trail.

NCE is deliberately narrow. It does not plan, reason about goals, or replace the agent. It
governs. The discipline of doing one thing — governance — well is what makes it trustworthy.

## Principles

1. **Governance is data, not code.** Rules live in versioned constitutions that can be
   reviewed, diffed, and rolled back — not scattered through application logic.
2. **Enforcement is independent of the model.** A confused, jailbroken, or adversarially
   prompted agent must not be able to grant itself permissions.
3. **Every decision is explainable.** A verdict without a reason is not acceptable in a
   governance system. Justifications are first-class.
4. **The audit trail is immutable.** History is the foundation of accountability; it must be
   append-only and tamper-evident.
5. **Fail closed, predictably.** When the engine is uncertain or unavailable, the safe
   default is to deny — and that behavior is explicit and configurable, never accidental.
6. **Runtime-agnostic.** NCE integrates with any agent framework through a clean API and
   SDKs; it is not coupled to a particular model or orchestration library.
7. **Performance is a feature.** Governance on the critical path must be fast enough that
   teams are never tempted to route around it.

## Who it is for

- **Platform and infrastructure teams** deploying agents and needing a consistent control
  plane across many use cases.
- **Compliance, risk, and security functions** that require provable, queryable records of
  agent behavior.
- **Agent and application developers** who want to externalize policy instead of hard-coding
  it.

## Non-goals

NCE intentionally does **not**:

- Build, train, or host language models.
- Act as an agent framework or orchestrator.
- Provide a general-purpose workflow engine.
- Guarantee that a model's *reasoning* is correct — it governs *actions*, not thoughts.
- Replace human judgment for decisions that should remain with humans; it can route such
  decisions to humans, but it is not a substitute for them.

## What success looks like

NCE succeeds when deploying an autonomous agent without an explicit, versioned constitution
feels as irresponsible as deploying a public service without authentication — and when
"show me why the agent did that" has a complete, trustworthy answer.

See [`architecture.md`](architecture.md) for how these principles become a system, and
[`roadmap.md`](roadmap.md) for how we get there.
