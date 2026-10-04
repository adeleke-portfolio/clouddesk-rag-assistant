# Lab 8 - Two-step pipeline: triage first, then reply
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal

# --- Load API key ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --- The form for the triage step ---
class TriageResult(BaseModel):
    category: Literal["billing", "login", "performance", "data_loss", "other"]
    sentiment: Literal["calm", "frustrated", "angry"]
    priority: Literal["low", "medium", "high", "urgent"]
    summary: str
    requires_human: bool
    suggested_team: Literal["billing_team", "engineering", "customer_success", "management"]


# --- STEP 1: Triage the complaint ---
def triage_ticket(complaint):
    prompt = f"""
You are a customer support triage system.
Analyze the complaint below and return a structured result.

Complaint: {complaint}
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TriageResult,
        ),
    )
    return TriageResult.model_validate_json(response.text)


# --- STEP 2: Write the reply, using the triage result as facts ---
def generate_reply(customer_name, complaint, ticket_number, triage):
    prompt = f"""
You are a senior customer support agent for CloudDesk.

Write a reply to the customer complaint below.

USE THESE FACTS (do not change them):
- Ticket number: {ticket_number}
- Category: {triage.category}
- Priority: {triage.priority}
- Suggested team: {triage.suggested_team}

RULES:
- Greet the customer by name: {customer_name}
- Apologize sincerely.
- Acknowledge the specific problem.
- State that this ticket is marked as {triage.priority} priority.
- State that the customer will hear back within 4 business hours.
- Sign as "The CloudDesk Team".

DO NOT:
- Promise a refund.
- Invent any fact not in this prompt.
- Use generic phrases like "we value your feedback".

CUSTOMER COMPLAINT:
{complaint}

REPLY:
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )
    return response.text


# --- Main pipeline ---
if __name__ == "__main__":
    customer_name = "Sarah"
    complaint = "I've been trying to log in for two days and keep getting an error. This is unacceptable."
    ticket_number = "CD-48220"

    # Step 1
    print("=== STEP 1: TRIAGE ===")
    triage = triage_ticket(complaint)
    print(f"Category:  {triage.category}")
    print(f"Sentiment: {triage.sentiment}")
    print(f"Priority:  {triage.priority}")
    print(f"Team:      {triage.suggested_team}")
    print(f"Human?     {triage.requires_human}")
    print(f"Summary:   {triage.summary}")

    # Step 2
    print("\n=== STEP 2: REPLY ===")
    reply = generate_reply(customer_name, complaint, ticket_number, triage)
    print(reply)