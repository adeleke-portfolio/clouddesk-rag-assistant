# Lab 15c - Customer complaint routing with LangGraph
import os
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

# --- Load the key ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
)


# --- Helper: extract text from a response, whether it is a string or list ---
def extract_text(response):
    content = response.content
    if isinstance(content, list):
        first = content[0]
        if isinstance(first, dict):
            return first.get("text", "")
        return str(first)
    return content


# --- 1. Define the state ---
class State(TypedDict):
    complaint: str
    category: str
    reply: str


# --- 2. Define the nodes ---

def classify(state: State):
    """Look at the complaint and decide the category."""
    prompt = f"""
Classify this customer complaint into ONE of these categories:
- billing
- login
- other

Complaint: {state['complaint']}

Return ONLY the category word. Nothing else.
"""
    response = model.invoke(prompt)
    category = extract_text(response).strip().lower()
    print(f"  [classify] -> {category}")
    return {"category": category}


def billing_handler(state: State):
    """Handle billing complaints."""
    print(f"  [billing_handler] handling: {state['complaint']}")
    prompt = f"""
You are a CloudDesk billing support agent.
Write a short, warm reply to this billing complaint.

Rules:
- Sign as "The CloudDesk Team".
- Do NOT promise a refund or credit.
- Do NOT invent an amount or a policy.
- Do NOT use placeholders like [Your Name].

Complaint: {state['complaint']}
"""
    response = model.invoke(prompt)
    return {"reply": extract_text(response).strip()}


def login_handler(state: State):
    """Handle login complaints."""
    print(f"  [login_handler] handling: {state['complaint']}")
    prompt = f"""
You are a CloudDesk login support agent.
Write a short, warm reply to this login complaint.

Rules:
- Sign as "The CloudDesk Team".
- Do NOT promise a refund or credit.
- Do NOT invent an amount or a policy.
- Do NOT use placeholders like [Your Name].

Complaint: {state['complaint']}
"""
    response = model.invoke(prompt)
    return {"reply": extract_text(response).strip()}


def general_handler(state: State):
    """Handle all other complaints."""
    print(f"  [general_handler] handling: {state['complaint']}")
    prompt = f"""
You are a CloudDesk customer support agent.
Write a short, warm reply to this complaint.

Rules:
- Sign as "The CloudDesk Team".
- Do NOT promise a refund or credit.
- Do NOT invent an amount or a policy.
- Do NOT use placeholders like [Your Name].

Complaint: {state['complaint']}
"""
    response = model.invoke(prompt)
    return {"reply": extract_text(response).strip()}


# --- 3. The routing decision ---

def route(state: State):
    """Return the name of the next node based on the category."""
    if state["category"] == "billing":
        return "billing_handler"
    elif state["category"] == "login":
        return "login_handler"
    else:
        return "general_handler"


# --- 4. Build the graph ---

builder = StateGraph(State)

builder.add_node("classify", classify)
builder.add_node("billing_handler", billing_handler)
builder.add_node("login_handler", login_handler)
builder.add_node("general_handler", general_handler)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route)

builder.add_edge("billing_handler", END)
builder.add_edge("login_handler", END)
builder.add_edge("general_handler", END)

graph = builder.compile()


# --- 5. Run it on two complaints ---

print("=== Test 1: Billing complaint ===")
result = graph.invoke({"complaint": "I was charged twice this month."})
print("Reply:", result["reply"])
print()

print("=== Test 2: Login complaint ===")
result = graph.invoke({"complaint": "I cannot log in. My password does not work."})
print("Reply:", result["reply"])