# Flagship Showcase: Autonomous DevOps Governance

This is a production-quality demonstration of the **Neural Constitution Engine (NCE)** regulating an autonomous DevOps agent.

## The Scenario

Imagine you have an autonomous AI agent responsible for deploying software into production. The agent decides what steps to take and generates an **Execution Plan** (a Directed Acyclic Graph of tasks).

However, AI agents are non-deterministic. Without guardrails, they might push risky changes directly to production, bypass Change Advisory Boards (CAB), or drop production databases during an upgrade.

The **Neural Constitution Engine** prevents this. The agent must submit its Execution Plan and every individual task to the NCE for evaluation against a declarative, deterministic **Constitution**.

## The Constitution

Our `constitution.yaml` mandates:
1. **CAB Approval:** Production deployments require CAB approval.
2. **Maintenance Windows:** Deployments can only happen during active maintenance windows.
3. **Rollback Plans:** Every production deployment must have a rollback plan.
4. **Security Criticals:** Software with critical vulnerabilities is completely blocked.
5. **Database Safety:** Production database migrations require manual approval.

## Running the Showcase Demo

You can run the full showcase natively via the Python SDK:

```bash
python demo.py
```

### What You Will See
The demo evaluates two execution plans:
1. **Compliant Plan:** The agent's plan correctly acquires approvals and follows all rules. NCE evaluates the DAG, steps through the nodes, and **ALLOWS** every action.
2. **Rejected Plan:** The agent attempts to deploy to production without CAB approval. NCE halts the pipeline by returning a **BLOCKED** verdict and a `CRITICAL` risk assessment on the final step.

## Using the API via Docker

You can also run this showcase as a microservice using the production FastAPI runtime.

1. Start the API using Docker Compose:
```bash
docker-compose up -d
```

2. Evaluate a valid Execution Plan via the API:
```bash
curl -X POST http://localhost:8000/plans/evaluate \
  -H "Content-Type: application/json" \
  -d @execution-plan.json
```

3. Evaluate a single rejected task via the API:
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d @requests/execution-plan-rejected_step_7.json
```

## Directory Structure

- `constitution.yaml`: The strict governance policy.
- `demo.py`: SDK demonstration script.
- `docker-compose.yml`: API microservice stack.
- `execution-plan.json`: The fully compliant DevOps DAG.
- `execution-plan-rejected.json`: The DAG attempting an unapproved production deploy.
- `requests/`: Individual `DecisionRequest` JSON files extracted from the plan for manual API testing.
- `expected-results/`: The output `AuditRecord` summaries expected for each step.
- `architecture.md`: Architecture diagrams showing how NCE fits into a CI/CD pipeline.
