import asyncio
from typing import Annotated

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


def add_audits(left, right):
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


class State(TypedDict):
    val: int
    audit_ids: Annotated[list[str], add_audits]


async def node(state):
    return {"val": 1, "audit_ids": ["123"]}


async def main():
    g = StateGraph(State)
    g.add_node("node", node)
    g.add_edge(START, "node")
    g.add_edge("node", END)
    app = g.compile()
    print(await app.ainvoke({"val": 0}))


asyncio.run(main())
