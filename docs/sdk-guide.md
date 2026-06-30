# SDK Guide

The SDK is the only officially supported interface to the core Neural Constitution Engine in Python.

## Engine Configuration

You can customize the SDK using the `EngineBuilder`:

```python
from backend.sdk.builder import EngineBuilder

engine = (
    EngineBuilder()
    .with_constitution("my-policy.yaml")
    .build()
)
```

## Evaluating Execution Plans

Execution plans represent Directed Acyclic Graphs (DAGs) of intended actions.

```python
from backend.sdk.types import ExecutionPlan, PlanNode, Edge

plan = ExecutionPlan(
    id="deploy-v2",
    nodes=(
        PlanNode(id="build", action=...),
        PlanNode(id="deploy", action=...)
    ),
    edges=(Edge(source="build", target="deploy"),)
)

result = engine.evaluate_plan(plan)

if result.is_valid:
    print("Plan is compliant and safe to execute.")
else:
    print("Plan blocked at node:", result.failed_node_id)
```
