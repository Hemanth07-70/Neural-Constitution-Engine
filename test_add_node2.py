import asyncio
from typing import TypedDict

from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    val: int


def my_node(state):
    return {"val": 1}


class MyMiddleware:
    def __init__(self, node):
        self.node = node

    async def __call__(self, state, config=None, **kwargs):
        if hasattr(self.node, "ainvoke"):
            return await self.node.ainvoke(state, config=config, **kwargs)
        return await self.node(state, config=config, **kwargs)


async def main():
    g = StateGraph(State)
    g.add_node("A", my_node)
    g.add_edge(START, "A")
    g.add_edge("A", END)

    spec = g.nodes["A"]
    # Wrap with RunnableLambda
    spec.runnable = RunnableLambda(MyMiddleware(spec.runnable))

    app = g.compile()
    print(await app.ainvoke({"val": 0}))


asyncio.run(main())
