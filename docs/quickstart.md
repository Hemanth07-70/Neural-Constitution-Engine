# Quickstart

Let's build a simple governance script that blocks any action with a critical vulnerability.

## 1. Create the Constitution
Save the following as `constitution.yaml`:

```yaml
apiVersion: nce/v1
kind: Constitution
metadata:
  id: quickstart
  version: 1.0.0
  scope: global
principles:
  - id: P1
    category: security
    statement: "No critical vulnerabilities."
rules:
  - id: R1
    principle: P1
    condition: "action.type == 'deploy' and action.params.vulns > 0"
    action:
      type: block
```

## 2. Run the Engine
Create `demo.py`:

```python
from backend.sdk.engine import Engine
from backend.sdk.types import Action, Actor, DecisionContext, DecisionRequest, Environment

engine = Engine.load("constitution.yaml")

request = DecisionRequest(
    actor=Actor(id="agent", type="machine"),
    action=Action(type="deploy", params={"vulns": 1}),
    context=DecisionContext(
        constitution_id="quickstart",
        environment=Environment(name="production")
    )
)

audit = engine.evaluate(request)
print("Verdict:", audit.result.action.value)
```

Run the script:
```bash
python demo.py
```
Output:
```
Verdict: block
```
