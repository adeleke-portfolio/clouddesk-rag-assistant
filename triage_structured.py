import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal

# Load the key
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --- The "Form" with locked-down choices ---
class TriageResult(BaseModel):
    category: Literal["billing", "login", "performance", "data_loss", "other"]
    sentiment: Literal["calm", "frustrated", "angry"]
    priority: Literal["low", "medium", "high", "urgent"]
    summary: str
    requires_human: bool
    suggested_team: Literal["billing_team", "engineering", "customer_success", "management"]


# --- The complaint ---
complaint = "I've been trying to log in for two days and keep getting an error. This is unacceptable."

# --- The prompt ---
prompt = f"""
You are a customer support triage system for CloudDesk.
Analyze the customer complaint and return a structured result.

Complaint: {complaint}
"""

# --- The API call with structured output ---
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=TriageResult,
    ),
)

print("=== RAW JSON RESPONSE ===")
print(response.text)

result = TriageResult.model_validate_json(response.text)

print("\n=== PARSED DATA ===")
print(f"Category: {result.category}")
print(f"Sentiment: {result.sentiment}")
print(f"Priority: {result.priority}")
print(f"Team: {result.suggested_team}")
print(f"Needs Human: {result.requires_human}")
print(f"Summary: {result.summary}")