# NCE DevOps Integration Architecture

This document describes how the Neural Constitution Engine (NCE) integrates with a modern, autonomous DevOps Agent.

## High Level Architecture

```mermaid
graph TD
    Agent[DevOps Agent] --> |Execution Plan| NCE[NCE API]
    NCE --> |Topological Sort & Validation| PlanVal[Plan Validator]
    PlanVal --> |Valid DAG| Engine[Governance Engine]
    Engine --> |Constitution Rules| Rules[(Constitution DB)]

    Agent --> |Executes Nodes| CI[CI/CD Pipeline]
    CI --> |Status| Agent
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Agent as DevOps Agent
    participant NCE as Neural Constitution Engine
    participant CI as CI/CD Infrastructure

    Agent->>NCE: POST /plans/evaluate (ExecutionPlan)
    NCE-->>Agent: PlanValidationResult (DAG structure valid)

    loop Over Topological Order
        Agent->>NCE: POST /evaluate (DecisionRequest)
        NCE->>NCE: Match Constitution Rules
        NCE->>NCE: Assess Risk & Resolve Conflicts
        NCE-->>Agent: AuditRecord (ALLOW/BLOCK)

        alt is ALLOWED
            Agent->>CI: Trigger Step
            CI-->>Agent: Step Complete
        else is BLOCKED
            Agent->>Agent: Halt Execution
        end
    end
```

## Explanation

1. **Autonomous Planning:** The agent synthesizes an `ExecutionPlan` which maps out dependencies (e.g., Build -> Unit Tests -> Deploy).
2. **Graph Validation:** NCE verifies that the plan is a valid Directed Acyclic Graph (DAG) and provides a safe execution order.
3. **Step-by-Step Governance:** Before taking any action on the CI/CD pipeline, the agent requests permission from the NCE.
4. **Enforcement:** If a critical rule (like requiring CAB approval for production) is violated, NCE issues a `BLOCK` verdict. The agent stops immediately, preventing risky deployments.
