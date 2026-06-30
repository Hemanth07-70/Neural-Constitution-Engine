# Public API Policy

The Neural Constitution Engine strictly follows **Semantic Versioning 2.0.0**.

## Stable APIs
The following APIs are considered stable. Breaking changes to these APIs will require a major version bump (e.g. `1.x.x` to `2.0.0`):

- **SDK facade (`backend/sdk/engine.py`):**
  - `Engine.load()`
  - `Engine.evaluate()`
  - `Engine.evaluate_plan()`
- **Core Types (`backend/sdk/types.py`):**
  - `DecisionRequest`
  - `Action`
  - `Actor`
  - `Environment`
  - `ExecutionPlan`
- **FastAPI Endpoints:**
  - `POST /evaluate`
  - `POST /plans/evaluate`

## Experimental APIs
The following features are experimental and their API surfaces may change in minor releases (`1.1.0`, `1.2.0`):

- The Plugin System (`backend/core/plugins/`)
- Dynamic Rule Injectors

Internal core modules (`backend/core/`) should not be imported directly. Always route logic through `backend.sdk`.
