# LangGraph Integration

The Neural Constitution Engine (NCE) seamlessly integrates with LangGraph, allowing autonomous AI agents to be governed by programmable constitutions.

This integration uses a proxy-pattern via the `GovernedGraph` class to automatically intercept node executions without altering your existing LangGraph code.

## Architecture

The integration exists entirely as an adapter layer on top of the NCE Application Layer. LangGraph depends on NCE, but NCE remains entirely independent of LangGraph.

```mermaid
sequenceDiagram
    participant Agent as LangGraph Agent
    participant Graph as GovernedGraph
    participant Middleware as GovernanceMiddleware
    participant Eval as EvaluationService
    participant NCE as SDK Engine

    Agent->>Graph: invoke(state)
    Graph->>Middleware: Node Execution
    Middleware->>Eval: evaluate_decision()
    Eval->>NCE: evaluate()
    NCE-->>Eval: AuditRecord
    Eval-->>Middleware: Verdict

    alt Verdict == ALLOW
        Middleware->>Agent: Execute Node
    else Verdict == BLOCK
        Middleware-->>Agent: Raise NodeBlockedException
    else Verdict == REWRITE
        Middleware->>Middleware: Apply payload to State
        Middleware->>Agent: Execute Node (Modified)
    else Verdict == REQUIRES_APPROVAL
        Middleware-->>Agent: Raise RequiresApprovalException
    end
```

## Quick Start

Wrap your `StateGraph` with `GovernedGraph` before compiling it.

```python
from langgraph.graph import StateGraph
from backend.integrations.langgraph import GovernedGraph, GovernedGraphConfig

# 1. Define your graph
graph = StateGraph(AgentState)
graph.add_node("GenerateCode", generate_code)
# ... add edges ...

# 2. Configure Governance
config = GovernedGraphConfig(
    organization_id="org-123",
    strict_mode=True
)

# 3. Wrap Graph
safe_graph = GovernedGraph(graph, eval_service, config)

# 4. Compile and Run
app = safe_graph.compile()
state = await app.ainvoke({"input": "task"})
```

## Verdict Handling

- **ALLOW**: Node executes normally.
- **BLOCK**: Halts graph execution immediately, raising `NodeBlockedException`.
- **REWRITE**: The NCE-provided payload is merged into the Graph State *before* the node executes.
- **REQUIRES_APPROVAL**: Raises `RequiresApprovalException` (can be configured to use LangGraph Native Checkpointers in the future).
- **LOG_ONLY**: Node executes normally, but a governance audit is recorded silently.
