# Architecture

The Neural Constitution Engine is composed of several isolated layers:

## 1. Domain Layer (`backend/core/domain/`)
The foundational models defining actions, actors, risk levels, and audit responses.

## 2. Constitution Layer (`backend/core/constitution/`)
Handles the loading, parsing, and validation of declarative policies (YAML/JSON).

## 3. Language Layer (`backend/core/language/`)
A pure-Python Recursive Descent parser and interpreter for the Constitution Expression Language DSL.

## 4. Evaluator Layer (`backend/core/evaluator/`)
A multi-stage pipeline:
- `MatcherStage`: Evaluates rules against the current request.
- `RiskStage`: Synthesizes a unified risk assessment.
- `ResolverStage`: Executes conflict resolution strategies.
- `ExplanationStage`: Builds human-readable AI explanations.
- `AuditStage`: Hashes and records the evaluation event.

## 5. SDK Layer (`backend/sdk/`)
Exposes a unified Builder pattern and facade (`Engine`) to interact with the system without exposing internal state.

## 6. API Layer (`backend/api/`)
A FastAPI wrapper mapping Pydantic schemas to the underlying SDK.
