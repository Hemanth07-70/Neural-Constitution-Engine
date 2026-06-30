import asyncio
from unittest.mock import AsyncMock, MagicMock

from langgraph.graph import END, START, StateGraph

from backend.integrations.langgraph.config import GovernedGraphConfig
from backend.integrations.langgraph.governed_graph import GovernedGraph
from backend.integrations.langgraph.state import GovernanceState


class DummyState(GovernanceState):
    value: int
    text: str


async def node_a(state: DummyState) -> dict:
    print("NODE A EXECUTED!")
    return {"value": state.get("value", 0) + 1}


async def main():
    eval_service = AsyncMock()
    mock_audit = MagicMock()
    mock_audit.result.verdict = "allow"
    mock_audit.id = "audit-123"
    eval_service.evaluate_decision.return_value = mock_audit

    config = GovernedGraphConfig(organization_id="test-org")

    graph = StateGraph(DummyState)
    graph.add_node("NodeA", node_a)
    graph.add_edge(START, "NodeA")
    graph.add_edge("NodeA", END)

    safe_graph = GovernedGraph(graph, eval_service, config)
    app = safe_graph.compile()

    state = await app.ainvoke({"value": 0, "text": ""})
    print("FINAL STATE:", state)


asyncio.run(main())
