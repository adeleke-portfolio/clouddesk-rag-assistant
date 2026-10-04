# CloudDesk RAG Assistant

An AI-powered customer support assistant that answers questions by retrieving information from a company policy document. It refuses to make up answers.

## The Problem

Customer support teams answer the same questions every day. Most AI chatbots guess at answers when they do not know the truth. That creates misinformation, angry customers, and legal risk.

## The Solution

This project uses **Retrieval-Augmented Generation (RAG)** to ground every answer in a real document. When a user asks a question, the app:

1. Turns the question into an embedding (a list of numbers).
2. Searches a vector database for the most relevant chunks of the policy.
3. Sends those chunks to the LLM with a strict instruction: "Answer using ONLY this context."
4. If the answer is not in the document, the AI says so instead of inventing one.

## Features

- **Document ingestion** - Loads and chunks a policy text file.
- **Semantic search** - Finds relevant text by meaning, not by keyword.
- **Grounded answers** - The AI only answers from the retrieved context.
- **Transparency** - The UI shows the exact chunks used to generate each answer.
- **Web interface** - Built with Streamlit for a clean, clickable experience.

## Tech Stack

- **Language:** Python 3.14
- **LLM:** Google Gemini (gemini-3.5-flash-lite)
- **Embeddings:** gemini-embedding-001
- **Vector Database:** ChromaDB
- **Web Framework:** Streamlit
- **Version Control:** Git and GitHub

## Project Structure

- `app_rag.py` - The Streamlit web app with RAG.
- `app.py` - Earlier version: triage and reply pipeline.
- `rag_pipeline.py` - Standalone RAG pipeline (terminal).
- `chroma_demo.py` - Vector database demo.
- `embeddings_demo.py` - First embedding experiment.
- `pipeline.py` - Two-step triage and reply pipeline.
- `triage_structured.py` - JSON structured output for triage.
- `email_generator.py` - Prompt-engineered email generator.
- `clouddesk_policy.txt` - Sample policy document used for RAG.

## How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/adeleke-portfolio/clouddesk-rag-assistant.git
   cd clouddesk-rag-assistant