# Lab 14b - LangChain RAG with a prompt template
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb
from google import genai

# --- Load the key ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Load the document and build Chroma ---
doc_path = Path(__file__).resolve().parent / "clouddesk_policy.txt"
with open(doc_path, "r", encoding="utf-8") as f:
    full_text = f.read()

chunks = [c.strip() for c in full_text.split("\n\n") if c.strip()]

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="policy")

for i, chunk in enumerate(chunks):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=chunk,
    )
    vector = result.embeddings[0].values
    collection.add(ids=[f"chunk_{i}"], documents=[chunk], embeddings=[vector])

# --- LangChain setup ---
model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a CloudDesk support agent. Answer ONLY using the context below. "
               "If the answer is not in the context, say you don't know.\n\nContext:\n{context}"),
    ("human", "{question}"),
])

chain = prompt | model | StrOutputParser()


# --- The RAG function ---
def ask(question):
    # Embed the question
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question,
    )
    query_vector = result.embeddings[0].values

    # Retrieve chunks
    results = collection.query(query_embeddings=[query_vector], n_results=3)
    context = "\n\n".join(results["documents"][0])

    # Run the chain with the context
    return chain.invoke({"context": context, "question": question})


# --- Test ---
print("Q: Can I get a refund after 45 days?")
print("A:", ask("Can I get a refund after 45 days?"))
print()
print("Q: Do you offer a free plan?")
print("A:", ask("Do you offer a free plan?"))