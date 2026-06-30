# Neural Constitution Engine (NCE)

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![CI Status](https://img.shields.io/badge/CI-Passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

**Neural Constitution Engine (NCE)** is a high-performance, deterministic policy evaluation framework designed to securely govern non-deterministic, autonomous AI agents. By requiring AI agents to validate execution plans (DAGs) against a declarative Constitution before they take action, NCE guarantees safety, compliance, and alignment.

## 🚀 Features

- **Deterministic Evaluation Pipeline:** Ensures fail-closed, purely deterministic evaluations.
- **Constitution Language (v1):** A bespoke, pure-Python DSL for creating expressive, highly-secure policy conditions.
- **DAG Execution Validation:** Built-in topological validation for complex AI execution graphs.
- **Conflict Resolution:** Configurable policies (e.g., `most-restrictive-wins`) to handle overlapping rules.
- **Extensible Architecture:** Designed with a robust plugin system for custom audit sinks and custom rule evaluators.
- **Multi-Runtime Support:** Native Python SDK, standalone FastAPI service, and a fully-featured CLI.

## 📦 Installation

NCE is distributed as a standard Python package.

```bash
pip install neural-constitution-engine
```

## ⚡ Quick Start

Create a policy (`constitution.yaml`):

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

Evaluate requests natively in Python:

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
print(audit.result.action) # VerdictAction.BLOCK
```

## 📖 Documentation

All documentation is located in the `docs/` directory:
- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [SDK Guide](docs/sdk-guide.md)
- [FastAPI Guide](docs/fastapi-guide.md)
- [CLI Guide](docs/cli-guide.md)
- [Constitution Language](docs/constitution-language.md)
- [Execution Plans](docs/execution-plans.md)
- [Plugin Development](docs/plugin-development.md)
- [Benchmarks](docs/benchmarks.md)

## 🤝 Contributing

We welcome community contributions! Please read our [SECURITY.md](SECURITY.md) and review our [Pull Request Checklist](.github/PULL_REQUEST_TEMPLATE.md) before submitting code.

## 📄 License

This project is licensed under the Apache 2.0 License.
