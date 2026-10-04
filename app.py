# Lab 9 - Streamlit web interface for the CloudDesk AI assistant
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal
import streamlit as st

# --- Load API key ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --- The triage form ---
class TriageResult(BaseModel):
    category: Literal["billing", "login", "performance", "data_loss", "other"]
    sentiment: Literal["calm", "frustrated", "angry"]
    priority: Literal["low", "medium", "high", "urgent"]
    summary: str
    requires_human: bool
    suggested_team: Literal["billing_team", "engineering", "customer_success", "management"]


# --- Triage function ---
import time

def triage_ticket(complaint):
    prompt = f"""
You are a customer support triage system.
Analyze the complaint below and return a structured result.

Complaint: {complaint}
"""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=TriageResult,
                ),
            )
            return TriageResult.model_validate_json(response.text)
        except Exception as e:
            if attempt == 2:
                raise  # If last attempt, raise the error
            time.sleep(2)  # Wait 2 seconds and retry

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
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2)


# ============================================================
# THE STREAMLIT APP STARTS HERE
# ============================================================

st.set_page_config(page_title="ADELEKE AI Assistant", page_icon="🤖")
st.title("🤖 ADELEKE CloudDesk AI Assistant")
st.write("Enter a customer complaint below. The AI will triage it and draft a reply.")

# --- Input fields ---
customer_name = st.text_input("Customer Name", value="Sarah")
ticket_number = st.text_input("Ticket Number", value="CD-48220")
complaint = st.text_area(
    "Customer Complaint",
    value="I've been trying to log in for two days and keep getting an error. This is unacceptable.",
    height=120,
)
# --- The button ---
if st.button("Process Complaint"):

    if not complaint.strip():
        st.warning("Please enter a complaint before clicking the button.")
    else:
        st.info("Step 1 of 2: Triaging the complaint. This can take 5-10 seconds...")
        progress = st.progress(0)

        with st.spinner("Calling the AI triage service..."):
            triage = triage_ticket(complaint)
        progress.progress(50)

        st.subheader("Step 1: Triage Result")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Category", triage.category)
            st.metric("Priority", triage.priority)
            st.metric("Sentiment", triage.sentiment)
        with col2:
            st.metric("Suggested Team", triage.suggested_team)
            st.metric("Needs Human Review", "Yes" if triage.requires_human else "No")
        st.write("**Full Summary:**", triage.summary)

        st.info("Step 2 of 2: Drafting the reply. This can take 5-10 seconds...")

        with st.spinner("Calling the AI reply service..."):
            reply = generate_reply(customer_name, complaint, ticket_number, triage)
        progress.progress(100)

        st.subheader("Step 2: AI-Drafted Reply")
        st.markdown(reply)
st.divider()
st.caption("Built with Streamlit + Gemini. This is a demo, not a real product.")