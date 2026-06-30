import asyncio
from collections.abc import Callable
from typing import Any

from langchain_core.runnables import RunnableConfig

from backend.application.services.evaluation_service import EvaluationService
from backend.integrations.langgraph.adapters import state_to_decision_request
from backend.integrations.langgraph.callbacks import GovernanceCallback
from backend.integrations.langgraph.config import GovernedGraphConfig
from backend.integrations.langgraph.exceptions import NodeBlockedException, RequiresApprovalException


class GovernanceMiddleware:
    """
    Wraps a LangGraph node executable. Intercepts the state, evaluates it using NCE,
    and then enforces the verdict before passing control to the actual node.
    """

    def __init__(
        self,
        node_name: str,
        original_node: Callable,
        eval_service: EvaluationService,
        config: GovernedGraphConfig,
        callback: GovernanceCallback | None = None,
    ):
        self.node_name = node_name
        self.original_node = original_node
        self.eval_service = eval_service
        self.config = config
        self.callback = callback

    async def __call__(self, state: dict[str, Any], config: RunnableConfig | None = None, **kwargs) -> Any:
        run_id = state.get("run_id", "unknown")
        if self.callback:
            self.callback.on_node_started(self.node_name, run_id)

        # 1. Build DecisionRequest
        request_schema = state_to_decision_request(self.node_name, state)

        # 2. Evaluate via EvaluationService
        try:
            audit = await self.eval_service.evaluate_decision(self.config.organization_id, request_schema)
        except Exception as e:
            if self.config.strict_mode:
                raise RuntimeError(f"Governance evaluation failed for node '{self.node_name}': {e}") from e
            # If not strict mode, allow execution to proceed if evaluation fails
            return await self._execute_node(state, config, **kwargs)

        verdict = audit.result.verdict

        # 3. Enforce Decision
        if verdict == "block":
            if self.callback:
                self.callback.on_node_blocked(self.node_name, audit.id, run_id, audit.explanation.summary)
            if self.config.stop_on_block:
                raise NodeBlockedException(self.node_name, audit.explanation.summary, audit.id)
            return self._inject_governance_state(state, audit.id, verdict)

        elif verdict == "rewrite":
            if self.callback:
                self.callback.on_node_rewritten(self.node_name, audit.id, run_id, state, audit.result.modified_payload)

            # Apply modified payload to state before executing node
            state.update(audit.result.modified_payload or {})

            node_result = await self._execute_node(state, config, **kwargs)

            # Inject rewrite history and governance state into the node's result
            if isinstance(node_result, dict):
                node_result = self._inject_governance_state(node_result, audit.id, verdict)
                if "rewrite_history" not in node_result:
                    node_result["rewrite_history"] = []
                node_result["rewrite_history"].append(
                    {"original": dict(state), "rewritten": audit.result.modified_payload}
                )
            return node_result

        elif verdict == "requires_approval":
            if self.callback:
                self.callback.on_node_paused(self.node_name, audit.id, run_id, audit.explanation.summary)
            raise RequiresApprovalException(self.node_name, audit.id, audit.explanation.summary)

        elif verdict in ("allow", "log_only"):
            if self.callback:
                self.callback.on_node_allowed(self.node_name, audit.id, run_id)
            node_result = await self._execute_node(state, config, **kwargs)
            res = self._inject_governance_state(node_result, audit.id, verdict)
            print("DEBUG MIDDLEWARE RETURN:", res)
            return res

        else:
            if self.config.strict_mode:
                raise NodeBlockedException(self.node_name, f"Unknown verdict: {verdict}", audit.id)
            node_result = await self._execute_node(state, config, **kwargs)
            res = self._inject_governance_state(node_result, audit.id, verdict)
            print("DEBUG MIDDLEWARE RETURN:", res)
            return res

    def _inject_governance_state(self, node_result: Any, audit_id: str, verdict: str) -> Any:
        """Injects governance metadata into the node's return dictionary."""
        if isinstance(node_result, dict):
            # Because LangGraph uses reducers for arrays, returning [audit_id] will append it.
            # If the node itself returned audit_ids, append to it.
            if "audit_ids" not in node_result:
                node_result["audit_ids"] = [audit_id]
            elif isinstance(node_result["audit_ids"], list):
                node_result["audit_ids"].append(audit_id)
            node_result["last_verdict"] = verdict
        return node_result

    async def _execute_node(self, state: dict[str, Any], config: RunnableConfig | None, **kwargs) -> Any:
        # If original_node is a LangGraph Runnable, we use ainvoke
        if hasattr(self.original_node, "ainvoke"):
            # Some runnables might not accept config in kwargs directly, but ainvoke handles it
            result = await self.original_node.ainvoke(state, config, **kwargs)
        elif asyncio.iscoroutinefunction(self.original_node):
            if config:
                result = await self.original_node(state, config, **kwargs)
            else:
                result = await self.original_node(state, **kwargs)
        else:
            # Wrap sync function in thread
            if config:
                result = await asyncio.to_thread(self.original_node, state, config, **kwargs)
            else:
                result = await asyncio.to_thread(self.original_node, state, **kwargs)

        run_id = state.get("run_id", "unknown")
        if self.callback:
            self.callback.on_node_completed(self.node_name, run_id)

        return result
