from collections.abc import Callable
from typing import Any

from langgraph.graph import StateGraph

from backend.application.services.evaluation_service import EvaluationService
from backend.integrations.langgraph.callbacks import DefaultGovernanceCallback, GovernanceCallback
from backend.integrations.langgraph.config import GovernedGraphConfig
from backend.integrations.langgraph.middleware import GovernanceMiddleware


class GovernedGraph:
    """
    A wrapper around LangGraph's StateGraph.
    Automatically injects NCE GovernanceMiddleware into every added node.
    """

    def __init__(
        self,
        graph: StateGraph,
        eval_service: EvaluationService,
        config: GovernedGraphConfig,
        callback: GovernanceCallback | None = None,
    ):
        self.graph = graph
        self.eval_service = eval_service
        self.config = config
        self.callback = callback or DefaultGovernanceCallback()

        # We need to wrap existing nodes if any exist
        self._wrap_existing_nodes()

        # Wrap `add_node` method of the underlying graph for future nodes.
        self._original_add_node = self.graph.add_node
        self.graph.add_node = self._governed_add_node

    def _wrap_existing_nodes(self):
        """Wraps any nodes that were already added to the graph before GovernedGraph was instantiated."""
        from langchain_core.runnables import RunnableLambda

        for node_name, node_spec in list(self.graph.nodes.items()):
            # In langgraph, nodes are typically NodeSpec objects holding a runnable
            original_runnable = getattr(node_spec, "runnable", node_spec)

            middleware = GovernanceMiddleware(
                node_name=node_name,
                original_node=original_runnable,
                eval_service=self.eval_service,
                config=self.config,
                callback=self.callback,
            )

            if hasattr(node_spec, "runnable"):
                node_spec.runnable = RunnableLambda(middleware)
            else:
                self.graph.nodes[node_name] = RunnableLambda(middleware)

    def _governed_add_node(self, node: str, action: Callable, **kwargs) -> StateGraph:
        """Wraps the node action in GovernanceMiddleware before adding to StateGraph."""

        middleware = GovernanceMiddleware(
            node_name=node,
            original_node=action,
            eval_service=self.eval_service,
            config=self.config,
            callback=self.callback,
        )

        return self._original_add_node(node, middleware, **kwargs)

    # Expose necessary properties and methods to act like StateGraph
    def add_edge(self, start_key: str, end_key: str) -> StateGraph:
        return self.graph.add_edge(start_key, end_key)

    def add_conditional_edges(self, *args, **kwargs) -> StateGraph:
        return self.graph.add_conditional_edges(*args, **kwargs)

    def set_entry_point(self, key: str) -> StateGraph:
        return self.graph.set_entry_point(key)

    def set_conditional_entry_point(self, *args, **kwargs) -> StateGraph:
        return self.graph.set_conditional_entry_point(*args, **kwargs)

    def set_finish_point(self, key: str) -> StateGraph:
        return self.graph.set_finish_point(key)

    def compile(self, *args, **kwargs) -> Any:
        # Before compiling, we can run any overall graph validation
        compiled_graph = self.graph.compile(*args, **kwargs)
        # We could also wrap the compiled graph's ainvoke/invoke to trigger graph-level callbacks
        return compiled_graph
