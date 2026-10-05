# Lab 15b - LangGraph with a conditional edge
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    number: int


def add_one(state: State):
    return {"number": state["number"] + 1}

def double(state: State):
    return {"number": state["number"] * 2}


def decide_next(state: State):
    """This function is the decision-maker. It returns the NAME of the next node."""
    if state["number"] < 10:
        return "double"
    else:
        return END


builder = StateGraph(State)
builder.add_node("add_one", add_one)
builder.add_node("double", double)

builder.add_edge(START, "add_one")
builder.add_conditional_edges("add_one", decide_next)
builder.add_edge("double", END)

graph = builder.compile()

print("Test 1 (starts at 5):")
print(graph.invoke({"number": 5}))

print("\nTest 2 (starts at 50):")
print(graph.invoke({"number": 50}))