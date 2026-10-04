# Lab 5 - My first LLM API call
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

env_path = Path(__file__).resolve().parent / ".env"
print("DEBUG: .env exists:", env_path.exists())

load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
print("DEBUG: api_key loaded =", api_key is not None)

client = genai.Client(api_key=api_key)

prompt = "In one sentence, explain what generative AI is to a 10-year-old."
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt,
)

print("Prompt:")
print(prompt)
print()
print("AI response:")
print(response.text)