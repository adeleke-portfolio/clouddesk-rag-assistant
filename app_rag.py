# Lab 13 - RAG inside Streamlit
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import chromadb
import streamlit as st

# --- Setup ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --- Helper functions ---
def embed(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values


@st.cache_resource
def build_collection(text):
    """Chunk, embed, and store the document. Cached so it only runs once."""
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="docs")

    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]

    for i, chunk in enumerate(chunks):
        vector = embed(chunk)
        collection.add(
            ids=[f"chunk_{i}"],
            documents=[chunk],
            embeddings=[vector],
        )

    return collection, len(chunks)


def ask(question, collection):
    query_vector = embed(question)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
    )
    chunks = results["documents"][0]
    context = "\n\n".join(chunks)

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

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )
    return chunks, response.text


# ============================================================
# THE APP
# ============================================================

st.set_page_config(page_title="CloudDesk RAG Assistant", page_icon="📚")
st.title("📚 CloudDesk RAG Assistant")
st.write("Ask questions about the CloudDesk policy. Answers are grounded in the document.")

# --- Load the document ---
doc_path = Path(__file__).resolve().parent / "clouddesk_policy.txt"
with open(doc_path, "r", encoding="utf-8") as f:
    document_text = f.read()

# --- Build the collection (cached) ---
with st.spinner("Loading and indexing the document..."):
    collection, chunk_count = build_collection(document_text)

st.success(f"Document loaded and indexed into {chunk_count} chunks.")

# --- The question box ---
question = st.text_input(
    "Ask a question",
    value="Can I get a refund after 45 days?",
)

# --- The button ---
if st.button("Ask"):

    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving relevant chunks..."):
            chunks, answer = ask(question, collection)

        # Show the retrieved context
        with st.expander("See the retrieved context (top 3 chunks)"):
            for i, chunk in enumerate(chunks):
                first_line = chunk.split("\n")[0]
                st.write(f"**[{i+1}]** {first_line}")
                st.caption(chunk[:200] + "...")

        # Show the answer
        st.subheader("Answer")
        st.markdown(answer)

st.divider()
st.caption("Built with Streamlit, Chroma, and Gemini.")