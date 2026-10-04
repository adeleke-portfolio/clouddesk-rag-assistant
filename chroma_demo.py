# Lab 11 - Storing and searching embeddings with Chroma
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import chromadb

# --- Setup ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Create a Chroma client and a collection ---
# A collection is like a table in a normal database.
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="company_docs")


# --- A helper to get an embedding from Google ---
def embed(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values


# --- Documents we want to store ---
documents = [
    "Our refund policy allows returns within 30 days of purchase.",
    "To reset your password, click 'Forgot Password' on the login page.",
    "We ship internationally to over 50 countries.",
    "Refunds are processed within 5 business days.",
    "For login issues, check that Caps Lock is not enabled.",
]

# --- Store them in Chroma ---
print("=== STORING DOCUMENTS ===\n")
for i, doc in enumerate(documents):
    vector = embed(doc)
    collection.add(
        ids=[f"doc_{i}"],
        documents=[doc],
        embeddings=[vector],
    )
    print(f"Stored doc_{i}: {doc}")

print(f"\nTotal documents in collection: {collection.count()}")


# --- Now search it ---
print("\n=== SEARCHING ===\n")

queries = [
    "How do I get my money back?",
    "I can't log in to my account.",
]

for query in queries:
    query_vector = embed(query)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2,
    )
    print(f"Query: {query}")
    print(f"Top matches:")
    for doc, distance in zip(results["documents"][0], results["distances"][0]):
        print(f"  - {doc}  (distance: {distance:.4f})")
    print()