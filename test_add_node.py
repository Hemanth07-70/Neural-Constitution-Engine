import asyncio
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    val: int


def my_node(state):
    return {"val": 1}


class MyMiddleware:
    def __init__(self, node):
        self.node = node

    async def __call__(self, state):
        res = (
            await asyncio.to_thread(self.node, state)
            if not asyncio.iscoroutinefunction(self.node)
            else await self.node(state)
        )
        # Langchain wrappers might be runnables, which don't just call directly if they need ainvoke.
        # But let's just see if we can call it.
        # But wait! If self.node is a RunnableCallable, it might require .ainvoke().
        if hasattr(self.node, "ainvoke"):
            return await self.node.ainvoke(state)
        return res


async def main():
    g = StateGraph(State)
    g.add_node("A", my_node)
    g.add_edge(START, "A")
    g.add_edge("A", END)

    spec = g.nodes["A"]
    spec.runnable = MyMiddleware(spec.runnable)

    app = g.compile()
    print(await app.ainvoke({"val": 0}))


asyncio.run(main())
