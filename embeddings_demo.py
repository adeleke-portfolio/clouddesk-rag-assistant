# Lab 10 - My first embedding
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Three sentences to embed
sentences = [
    "How do I get my money back?",
    "What is your refund policy?",
    "How do I reset my password?",
]

print("=== GENERATING EMBEDDINGS ===\n")

embeddings = []
for sentence in sentences:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=sentence,
    )
    vector = result.embeddings[0].values
    embeddings.append(vector)
    print(f"Sentence: {sentence}")
    print(f"Embedding length: {len(vector)} numbers")
    print(f"First 5 numbers: {vector[:5]}")
    print()

# Compare the sentences
print("=== COMPARING SENTENCES ===\n")

# A small helper that computes similarity between two lists of numbers
def similarity(a, b):
    # Dot product divided by the lengths of each vector
    dot = sum(x * y for x, y in zip(a, b))
    len_a = sum(x * x for x in a) ** 0.5
    len_b = sum(y * y for y in b) ** 0.5
    return dot / (len_a * len_b)

sim_1_2 = similarity(embeddings[0], embeddings[1])
sim_1_3 = similarity(embeddings[0], embeddings[2])
sim_2_3 = similarity(embeddings[1], embeddings[2])

print(f"Similarity between sentence 1 and 2 (money back vs refund):  {sim_1_2:.4f}")
print(f"Similarity between sentence 1 and 3 (money back vs password): {sim_1_3:.4f}")
print(f"Similarity between sentence 2 and 3 (refund vs password):     {sim_2_3:.4f}")