"""
rag.py — RAG (Retrieval-Augmented Generation) pipeline for NayePankh AI Hub

Flow:
  1. Load all .txt files from knowledge/ folder → split into paragraphs (chunks)
  2. Embed all chunks into vectors at startup (runs once)
  3. search_knowledge(query) → finds top-k most similar chunks → returns as string
     This string becomes the context passed to the LLM.
"""

# ─────────────────────────────────────────────
# SECTION 1 — IMPORTS
# ─────────────────────────────────────────────
import os
import torch
from sentence_transformers import SentenceTransformer, util


# ─────────────────────────────────────────────
# SECTION 2 — LOAD THE MODEL
# ─────────────────────────────────────────────
# Runs once when this file is imported.
# First run downloads ~90MB model; subsequent runs load from local cache.
model = SentenceTransformer('all-MiniLM-L6-v2')


# ─────────────────────────────────────────────
# SECTION 3 — LOAD AND CHUNK THE KNOWLEDGE BASE
# ─────────────────────────────────────────────
def load_knowledge_base() -> list[str]:
    """
    Reads all .txt files from the knowledge/ folder (relative to this file).
    Splits each file into paragraphs (double-newline separated).
    Returns a flat list of non-empty paragraph strings.
    """
    knowledge_dir = os.path.join(os.path.dirname(__file__), "knowledge")
    chunks = []

    for filename in os.listdir(knowledge_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(knowledge_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by paragraph (double newline)
            paragraphs = content.split("\n\n")
            for paragraph in paragraphs:
                stripped = paragraph.strip()
                if stripped:  # Skip empty strings
                    chunks.append(stripped)

    return chunks


# ─────────────────────────────────────────────
# SECTION 4 — BUILD THE INDEX (runs at import time)
# ─────────────────────────────────────────────
# Load all knowledge paragraphs into memory
chunks = load_knowledge_base()

# Encode every chunk into a vector — this is our searchable index
chunk_embeddings = model.encode(chunks, convert_to_tensor=True)


# ─────────────────────────────────────────────
# SECTION 5 — THE SEARCH FUNCTION
# ─────────────────────────────────────────────
def search_knowledge(query: str, top_k: int = 3) -> str:
    """
    Finds the top_k most semantically similar chunks to the query.

    Args:
        query:  The user's question or message.
        top_k:  Number of best-matching paragraphs to return (default 3).

    Returns:
        A single string of the top_k chunks joined by double newlines.
        This is the context passed to the LLM to ground its answer.
    """
    # Encode the query into the same vector space as the chunks
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarity between query and all chunk embeddings
    scores = util.cos_sim(query_embedding, chunk_embeddings)

    # Get indices of the top_k highest-scoring chunks
    top_results = torch.topk(scores, k=min(top_k, len(chunks)))
    top_indices = top_results.indices[0].tolist()

    # Collect the matching text chunks
    top_chunks = [chunks[i] for i in top_indices]

    # Join and return as a single context string
    return "\n\n".join(top_chunks)
