# Lab 12 - Full RAG pipeline
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import chromadb

# --- Setup ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="clouddesk_policy")


def embed(text):
    """Turn text into an embedding (list of numbers)."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values


# ============================================================
# STEP 1: LOAD THE DOCUMENT
# ============================================================
print("=== STEP 1: LOADING DOCUMENT ===\n")

doc_path = Path(__file__).resolve().parent / "clouddesk_policy.txt"
with open(doc_path, "r", encoding="utf-8") as f:
    full_text = f.read()

print(f"Loaded {len(full_text)} characters from clouddesk_policy.txt")


# ============================================================
# STEP 2: SPLIT INTO CHUNKS
# ============================================================
print("\n=== STEP 2: SPLITTING INTO CHUNKS ===\n")

# Split on double newlines (blank lines between sections)
chunks = [c.strip() for c in full_text.split("\n\n") if c.strip()]

print(f"Created {len(chunks)} chunks:")
for i, chunk in enumerate(chunks):
    first_line = chunk.split("\n")[0]
    print(f"  Chunk {i}: {first_line[:60]}...")


# ============================================================
# STEP 3: EMBED AND STORE
# ============================================================
print("\n=== STEP 3: EMBEDDING AND STORING ===\n")

for i, chunk in enumerate(chunks):
    vector = embed(chunk)
    collection.add(
        ids=[f"chunk_{i}"],
        documents=[chunk],
        embeddings=[vector],
    )
    print(f"Stored chunk_{i}")

print(f"\nTotal chunks stored: {collection.count()}")


# ============================================================
# STEP 4: ASK A QUESTION
# ============================================================
print("\n=== STEP 4: ASKING QUESTIONS ===\n")


def ask(question):
    """The full RAG flow: retrieve chunks, then generate an answer."""
    print(f"QUESTION: {question}\n")

    # 1. Embed the question
    query_vector = embed(question)

    # 2. Retrieve the top 3 most relevant chunks
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
    )
    retrieved_chunks = results["documents"][0]

    print("RETRIEVED CONTEXT:")
    for i, chunk in enumerate(retrieved_chunks):
        first_line = chunk.split("\n")[0]
        print(f"  [{i+1}] {first_line[:60]}...")
    print()

    # 3. Build the prompt with the retrieved context
    context = "\n\n".join(retrieved_chunks)
    prompt = f"""
You are a CloudDesk customer support agent.
Answer the customer's question using ONLY the information in the context below.
If the answer is not in the context, say "I don't have that information. Please contact support."

CONTEXT:
{context}

CUSTOMER QUESTION:
{question}

ANSWER:
"""

    # 4. Send to the LLM
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    print("ANSWER:")
    print(response.text)
    print("\n" + "=" * 60 + "\n")


# --- Test questions ---
ask("Can I get a refund after 45 days?")
ask("How do I reset my password?")
ask("Do you offer a free plan?")