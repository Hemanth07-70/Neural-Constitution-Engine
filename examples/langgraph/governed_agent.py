from typing import Any

from langgraph.graph import END, START, StateGraph

from backend.application.services.evaluation_service import EvaluationService
from backend.integrations.langgraph.config import GovernedGraphConfig
from backend.integrations.langgraph.governed_graph import GovernedGraph
from backend.integrations.langgraph.state import GovernanceState


# Extend GovernanceState so we automatically get audit tracking
class AgentState(GovernanceState):
    repo_content: str
    patch_generated: str
    tests_passed: bool
    critical_vulns: int
    rollback_plan: str
    deploy_status: str


# --- Nodes ---


async def read_repo(state: AgentState) -> AgentState:
    state["repo_content"] = "print('hello world')"
    return state


async def generate_patch(state: AgentState) -> AgentState:
    state["patch_generated"] = "+ print('hello universe')"
    return state


async def run_tests(state: AgentState) -> AgentState:
    # Simulate tests passing
    state["tests_passed"] = True
    return state


async def security_scan(state: AgentState) -> AgentState:
    # Simulate finding 0 vulnerabilities
    state["critical_vulns"] = 0
    return state


async def deploy(state: AgentState) -> AgentState:
    # At this point, the Constitution will have verified tests_passed and critical_vulns
    # and might have injected a rollback_plan if one didn't exist!
    state["deploy_status"] = "Success"
    return state


# --- Graph Definition ---


def create_agent(eval_service: EvaluationService, org_id: str) -> Any:
    # 1. Define standard LangGraph StateGraph
    graph = StateGraph(AgentState)

    # 2. Add nodes (Note the names match the action.type in Constitution)
    graph.add_node("ReadRepository", read_repo)
    graph.add_node("GeneratePatch", generate_patch)
    graph.add_node("RunTests", run_tests)
    graph.add_node("SecurityScan", security_scan)
    graph.add_node("Deploy", deploy)

    # 3. Add edges
    graph.add_edge(START, "ReadRepository")
    graph.add_edge("ReadRepository", "GeneratePatch")
    graph.add_edge("GeneratePatch", "RunTests")
    graph.add_edge("RunTests", "SecurityScan")
    graph.add_edge("SecurityScan", "Deploy")
    graph.add_edge("Deploy", END)

    # 4. Wrap with GovernedGraph
    config = GovernedGraphConfig(
        organization_id=org_id,
        strict_mode=True,
    )

    safe_graph = GovernedGraph(graph, eval_service, config)

    # 5. Compile the graph
    return safe_graph.compile()
