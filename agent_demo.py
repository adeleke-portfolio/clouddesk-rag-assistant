# Lab 16 - AI Agent with Tool Calling
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

# --- Load the key ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def extract_text(response):
    """Extract plain text from a response, whether content is a string or a list."""
    content = response.content
    if isinstance(content, list):
        first = content[0]
        if isinstance(first, dict):
            return first.get("text", "")
        return str(first)
    return content
# ============================================================
# STEP 1: DEFINE THE TOOLS
# ============================================================

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression. Use this for any math.

    Args:
        expression: A Python math expression like "2 + 2" or "10 * 5"

    Returns:
        The result of the calculation
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: The city name, like "San Francisco" or "London"

    Returns:
        The weather description
    """
    # Mock implementation - in a real app you would call a weather API
    weather_data = {
        "san francisco": "Foggy, 60°F",
        "london": "Rainy, 55°F",
        "new york": "Sunny, 72°F",
        "lagos": "Hot and humid, 90°F",
    }
    key = location.lower().strip()
    if key in weather_data:
        return f"The weather in {location} is: {weather_data[key]}"
    return f"I don't have weather data for {location}."


@tool
def get_customer_info(customer_id: str) -> str:
    """Look up a customer by their ID.

    Args:
        customer_id: The customer's ID, like "C-1001"

    Returns:
        The customer's name and plan
    """
    customers = {
        "C-1001": {"name": "Alice Johnson", "plan": "Enterprise"},
        "C-1002": {"name": "Bob Smith", "plan": "Basic"},
        "C-1003": {"name": "Charlie Brown", "plan": "Pro"},
    }
    if customer_id in customers:
        c = customers[customer_id]
        return f"Customer {customer_id}: {c['name']}, plan: {c['plan']}"
    return f"Customer {customer_id} not found."


# Collect all tools in a list
tools = [calculate, get_weather, get_customer_info]


# ============================================================
# STEP 2: DEFINE THE AGENT STATE
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ============================================================
# STEP 3: CREATE THE MODEL AND BIND THE TOOLS
# ============================================================

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Bind the tools to the model so it knows what it can call
model_with_tools = model.bind_tools(tools)


# ============================================================
# STEP 4: DEFINE THE AGENT NODE
# ============================================================

def agent_node(state: AgentState) -> dict:
    """The agent decides what to do next: call a tool or respond."""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


# ============================================================
# STEP 5: DEFINE THE TOOL EXECUTION NODE
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# STEP 6: DEFINE THE ROUTING LOGIC
# ============================================================

def should_continue(state: AgentState) -> str:
    """Decide whether to call a tool or stop."""
    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM asked for a tool call, go to the tool node
    if getattr(last_message, "tool_calls", None):
        return "tools"

    # Otherwise, the agent is done
    return "end"


# ============================================================
# STEP 7: BUILD THE GRAPH
# ============================================================

builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {
    "tools": "tools",
    "end": END,
})
builder.add_edge("tools", "agent")

graph = builder.compile()


# ============================================================
# STEP 8: RUN THE AGENT
# ============================================================

def run_agent(question: str):
    print(f"QUESTION: {question}")
    print("-" * 60)

    initial_state = {"messages": [HumanMessage(content=question)]}

    for event in graph.stream(initial_state, stream_mode="values"):
        last = event["messages"][-1]

        # Show what the agent decided
        if hasattr(last, "tool_calls") and last.tool_calls:
            for tc in last.tool_calls:
                print(f"  [AGENT DECIDED] Call tool: {tc['name']}({tc['args']})")

        # Show tool results
        if isinstance(last, ToolMessage):
            print(f"  [TOOL RESULT]  {last.content}")

    print()
    print("FINAL ANSWER:")
    print(extract_text(last))
    print("=" * 60)
    print()


# --- Test with three questions ---
run_agent("What is 25 * 48?")
run_agent("What's the weather in Lagos?")
run_agent("I need to know the plan for customer C-1003, and also what is 100 / 4?")