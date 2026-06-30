# Execution Plans

Neural Constitution Engine supports evaluating DAGs (Directed Acyclic Graphs) of AI actions, known as an `ExecutionPlan`.

## Validating Plans

When a plan is evaluated, NCE:
1. Validates the plan is a valid DAG (no circular dependencies or cycles).
2. Performs a Topological Sort.
3. Iterates over the sorted plan, evaluating each `PlanNode` individually against the Constitution.
4. If *any* node is blocked, the engine aborts and halts the plan.

## JSON Schema

```json
{
  "id": "deploy-v2-production",
  "nodes": [
    {
      "id": "step-1",
      "action": {
        "type": "build",
        "params": {}
      }
    }
  ],
  "edges": []
}
```
