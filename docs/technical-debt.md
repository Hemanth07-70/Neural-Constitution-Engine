# Technical Debt Register

This document tracks known technical debt, suboptimal implementations, and areas requiring refactoring in the Neural Constitution Engine (as of v0.1.0-alpha).

## 1. Plugin Discovery Stub
- **Location**: `backend/sdk/builder.py`
- **Issue**: The SDK's `EngineBuilder` iterates over `config.plugin_dirs` but currently contains a `pass` stub instead of an actual file-system discovery and dynamic import mechanism (e.g., using `importlib`).
- **Impact**: Custom external plugins cannot be dynamically loaded by directory path yet; they must be manually registered.
- **Recommendation**: Implement `importlib.metadata` entry points or a recursive module scanner in the `PluginManager`.

## 2. Registry Coupling in Pipeline
- **Location**: `backend/sdk/engine.py` / `backend/core/evaluator/pipeline.py`
- **Issue**: The `EvaluationPipeline.evaluate()` method currently accepts the entire `PluginManager` as a `registry` argument to resolve contexts/evaluators.
- **Impact**: Leaks the `PluginManager` interface into the pipeline, slightly violating the separation of concerns.
- **Recommendation**: Introduce a `RegistryFacade` or explicitly pass the required isolated `CapabilityRegistry` instances to the pipeline instead of the entire manager.

## 3. Duplicate Abstractions
- **Location**: `backend/core/constitution/rule.py` vs. `backend/core/rules/interfaces.py`
- **Issue**: A `Rule` is loaded as a pure dataclass, but its execution logic is handled by disparate `RuleMatcher` and `RuleEvaluator` interfaces.
- **Impact**: Minimal, but requires the `MatcherStage` to carefully map the data object to the executable plugin.
- **Recommendation**: Maintain the separation (data vs. behavior is good), but ensure comprehensive documentation explains how a rule ID maps to a specific evaluator plugin.

## 4. Test Coverage for Edge Cases
- **Location**: `backend/tests/`
- **Issue**: While the happy paths and primary graph validation paths are well-tested, deep fuzzy testing of the YAML parser (e.g., handling malformed Unicode, extremely deeply nested JSON) is missing.
- **Impact**: Low risk due to `yaml.safe_load`, but robustness could be improved.
- **Recommendation**: Integrate `hypothesis` for property-based testing of the domain models and loaders.

## 5. Breaking Changes to Avoid
When addressing this debt, maintainers must **AVOID**:
1. Removing `@dataclass(frozen=True)` from any `domain` or `planner` objects. Mutability will break thread-safety.
2. Introducing asynchronous (`async/await`) code into the core pipeline. The kernel must remain synchronous and deterministic; orchestrators can wrap it in async executors if needed.
3. Exposing `backend.core` modules through `backend.sdk`. The facade must remain strictly enforced.
