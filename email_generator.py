# Lab 6 v5 - Email generator, clean version
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_reply(customer_name, complaint, ticket_number, priority, response_time):
    """Generate a customer support email draft for a given complaint."""
    prompt = f"""
You are a senior customer support agent for CloudDesk, a cloud storage company.

Write a reply to the customer complaint below.

GREETING RULES:
- Open with a warm, personal greeting that uses the customer's first name.
- Do NOT open with "Hi there" or "Dear Sir/Madam".
- Do NOT ask "how may I help you" — the customer already explained the problem.

BODY RULES:
- Apologize sincerely.
- Acknowledge the specific problem.
- If the customer mentions billing, acknowledge the financial concern.
- Offer one clear, concrete next step.

NEGATIVE CONSTRAINTS (do NOT do these):
- Do NOT promise or imply a refund.
- Do NOT invent a ticket number. Use only: {ticket_number}
- Do NOT invent a phone number, URL, or policy.
- Do NOT misspell or alter the customer's name. Use exactly: {customer_name}
- Do NOT use generic phrases like "we value your feedback".
- Do NOT describe or imply the customer's "work", "business", or "team" unless they mentioned it.

CLOSING RULES:
- Sign as "The CloudDesk Team".

CUSTOMER DETAILS:
- Name: {customer_name}
- Ticket: {ticket_number}
- Priority: {priority}
- Expected response time: {response_time}

CUSTOMER COMPLAINT:
{complaint}

REPLY:
"""

    for attempt in range(1, 6):
        try:
            response = client.models.generate_content(
                model="models/gemini-3.1-flash-lite",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print(f"Attempt {attempt} failed: {type(e).__name__}")
            if attempt == 5:
                raise
            time.sleep(attempt * 3)


if __name__ == "__main__":
    print(generate_reply(
        customer_name="Test",
        complaint="This is a test complaint.",
        ticket_number="CD-00000",
        priority="low",
        response_time="24 hours",
    ))