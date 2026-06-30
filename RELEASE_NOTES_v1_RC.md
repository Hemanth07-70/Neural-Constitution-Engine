# Neural Constitution Engine v1.0.0-rc1

We are thrilled to announce the first Release Candidate for the Neural Constitution Engine (NCE)!

## Highlights

- **Pure-Python Evaluator:** No `eval()`, no external C-extensions. Safe, deterministic execution for agent policies.
- **DAG Governance:** Integrated validation of Execution Plans (Directed Acyclic Graphs).
- **FastAPI Ready:** Deploy instantly as an HTTP microservice.
- **Sub-millisecond Latency:** Average evaluation times of ~5 microseconds per rule.

## Breaking Changes from Alpha
- SDK usage is now fully decoupled from Core execution.
- Rules now accept string conditions using the new NCE Constitution Expression Language instead of raw dictionaries.

## What's Next
- Gathering feedback on the Expression Language.
- Stabilizing the Plugin architecture.
- Finalizing v1.0.0.
