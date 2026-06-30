from typing import Any, Protocol


class GovernanceCallback(Protocol):
    """Callback protocol for governance events in a LangGraph run."""

    def on_graph_started(self, graph_name: str, run_id: str, **kwargs: Any) -> None:
        ...

    def on_node_started(self, node_name: str, run_id: str, **kwargs: Any) -> None:
        ...

    def on_node_allowed(self, node_name: str, audit_id: str, run_id: str, **kwargs: Any) -> None:
        ...

    def on_node_blocked(self, node_name: str, audit_id: str, run_id: str, reason: str, **kwargs: Any) -> None:
        ...

    def on_node_rewritten(
        self, node_name: str, audit_id: str, run_id: str, original: Any, rewritten: Any, **kwargs: Any
    ) -> None:
        ...

    def on_node_paused(self, node_name: str, audit_id: str, run_id: str, reason: str, **kwargs: Any) -> None:
        ...

    def on_node_completed(self, node_name: str, run_id: str, **kwargs: Any) -> None:
        ...

    def on_graph_completed(self, graph_name: str, run_id: str, **kwargs: Any) -> None:
        ...

    def on_graph_failed(self, graph_name: str, run_id: str, error: Exception, **kwargs: Any) -> None:
        ...


class DefaultGovernanceCallback(GovernanceCallback):
    """A default implementation that just logs to stdout."""

    def on_graph_started(self, graph_name: str, run_id: str, **kwargs: Any) -> None:
        pass

    def on_node_started(self, node_name: str, run_id: str, **kwargs: Any) -> None:
        pass

    def on_node_allowed(self, node_name: str, audit_id: str, run_id: str, **kwargs: Any) -> None:
        pass

    def on_node_blocked(self, node_name: str, audit_id: str, run_id: str, reason: str, **kwargs: Any) -> None:
        pass

    def on_node_rewritten(
        self, node_name: str, audit_id: str, run_id: str, original: Any, rewritten: Any, **kwargs: Any
    ) -> None:
        pass

    def on_node_paused(self, node_name: str, audit_id: str, run_id: str, reason: str, **kwargs: Any) -> None:
        pass

    def on_node_completed(self, node_name: str, run_id: str, **kwargs: Any) -> None:
        pass

    def on_graph_completed(self, graph_name: str, run_id: str, **kwargs: Any) -> None:
        pass

    def on_graph_failed(self, graph_name: str, run_id: str, error: Exception, **kwargs: Any) -> None:
        pass
