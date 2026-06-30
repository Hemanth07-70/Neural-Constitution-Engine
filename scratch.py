import asyncio
from typing import Annotated

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


def add_audits(left, right):
    print(f"REDUCER left={left} right={right}")
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


class State(TypedDict):
    value: int
    audit_ids: Annotated[list[str], add_audits]


async def node_a(state: State):
    return {"value": 1, "audit_ids": ["123"]}


async def main():
    g = StateGraph(State)
    g.add_node("A", node_a)
    g.add_edge(START, "A")
    g.add_edge("A", END)
    app = g.compile()
    res = await app.ainvoke({"value": 0})
    print(res)


asyncio.run(main())
