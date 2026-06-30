from unittest.mock import AsyncMock, MagicMock

import pytest
from langgraph.graph import END, START, StateGraph

from backend.integrations.langgraph.config import GovernedGraphConfig
from backend.integrations.langgraph.exceptions import NodeBlockedException
from backend.integrations.langgraph.governed_graph import GovernedGraph
from backend.integrations.langgraph.state import GovernanceState


# Dummy State
class DummyState(GovernanceState):
    value: int
    text: str


# Dummy Nodes
async def node_a(state: DummyState) -> dict:
    return {"value": state.get("value", 0) + 1}


async def node_b(state: DummyState) -> dict:
    return {"text": "done"}


@pytest.fixture
def eval_service():
    return AsyncMock()


@pytest.fixture
def config():
    return GovernedGraphConfig(organization_id="test-org")


@pytest.mark.asyncio
async def test_governed_graph_allow(eval_service, config):
    # Setup mock to ALLOW
    mock_audit = MagicMock()
    mock_audit.result.verdict = "allow"
    mock_audit.id = "audit-123"
    eval_service.evaluate_decision.return_value = mock_audit

    graph = StateGraph(DummyState)
    graph.add_node("NodeA", node_a)
    graph.add_edge(START, "NodeA")
    graph.add_edge("NodeA", END)

    safe_graph = GovernedGraph(graph, eval_service, config)
    app = safe_graph.compile()

    state = await app.ainvoke({"value": 0, "text": ""})

    # Assert node ran
    assert state["value"] == 1
    # Assert audit was recorded
    assert "audit-123" in state.get("audit_ids", [])
    assert eval_service.evaluate_decision.called


@pytest.mark.asyncio
async def test_governed_graph_block(eval_service, config):
    # Setup mock to BLOCK
    mock_audit = MagicMock()
    mock_audit.result.verdict = "block"
    mock_audit.explanation.summary = "Not allowed"
    mock_audit.id = "audit-123"
    eval_service.evaluate_decision.return_value = mock_audit

    graph = StateGraph(DummyState)
    graph.add_node("NodeA", node_a)
    graph.add_edge(START, "NodeA")
    graph.add_edge("NodeA", END)

    safe_graph = GovernedGraph(graph, eval_service, config)
    app = safe_graph.compile()

    with pytest.raises(NodeBlockedException) as excinfo:
        await app.ainvoke({"value": 0, "text": ""})

    assert "Not allowed" in str(excinfo.value)


@pytest.mark.asyncio
async def test_governed_graph_rewrite(eval_service, config):
    # Setup mock to REWRITE
    mock_audit = MagicMock()
    mock_audit.result.verdict = "rewrite"
    mock_audit.result.modified_payload = {"value": 100}
    mock_audit.id = "audit-123"
    eval_service.evaluate_decision.return_value = mock_audit

    graph = StateGraph(DummyState)
    graph.add_node("NodeA", node_a)
    graph.add_edge(START, "NodeA")
    graph.add_edge("NodeA", END)

    safe_graph = GovernedGraph(graph, eval_service, config)
    app = safe_graph.compile()

    state = await app.ainvoke({"value": 0, "text": ""})

    # The payload changed value to 100 before node_a ran, then node_a adds 1
    assert state["value"] == 101
    assert len(state["rewrite_history"]) == 1
    assert state["rewrite_history"][0]["rewritten"] == {"value": 100}
