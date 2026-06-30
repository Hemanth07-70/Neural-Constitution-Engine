# Security Review

A comprehensive security review of the Neural Constitution Engine codebase was conducted ahead of v1.0.0.

## 1. Expression Language Safety (No RCE)
A critical requirement was replacing dictionary-based exact matches with a rich policy DSL without introducing Remote Code Execution (RCE).
- **Findings:** The AST is constructed using a hand-written Recursive Descent parser. The `LanguageEvaluator` only resolves field paths dynamically from `EvaluationContext.request`.
- **Verdict:** Secure. No use of `eval()`, `exec()`, or `getattr` chains capable of escaping the context sandbox.

## 2. Plugin Isolation
The `PluginManager` discovers and dynamically loads python files from user-defined directories.
- **Findings:** Because plugins are arbitrary Python scripts, they inherent the security context of the host process. NCE mitigates impact by forcing plugins to interact exclusively with the `RuleRegistry` facade (which restricts mutability).
- **Verdict:** Secure by design, but system operators must ensure the plugin directory is properly locked down via host file permissions (e.g. `chmod 755`), as malicious plugins can theoretically bypass Python's runtime constraints.

## 3. Dependency Supply Chain
- **Findings:** The project relies heavily on `pydantic`, `fastapi`, and native python libraries. Dependabot and CodeQL are enabled in `.github/workflows`.
- **Verdict:** Secure.

## 4. Default Fail-Closed
- **Findings:** Evaluator pipeline strictly defaults to `block` if a deterministic resolution cannot be made, or if errors occur during DAG validation.
- **Verdict:** Secure. Strict zero-trust paradigm holds.
