# Lab 14 - LangChain fundamentals
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Load the key ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- Step 1: Create the model ---
model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# --- Step 2: Create a prompt template ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} for {company}. Reply in one sentence."),
    ("human", "{question}"),
])

# --- Step 3: Create an output parser ---
parser = StrOutputParser()

# --- Step 4: Chain them together with the pipe operator ---
chain = prompt | model | parser

# --- Step 5: Invoke the chain ---
result = chain.invoke({
    "role": "customer support agent",
    "company": "CloudDesk",
    "question": "Can I get a refund after 45 days?",
})

print(result)