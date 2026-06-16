"""
rag.py — Lightweight Knowledge Search for NayePankh AI Hub

Since the knowledge base is extremely small (a few KB), we do not need heavy
machine learning models (like PyTorch or SentenceTransformers) to chunk and
semantically search the text. 

This module simply loads all the raw text from the knowledge/ folder and 
returns it directly to the LLM as context.
"""

import os

def search_knowledge(query: str, top_k: int = 3) -> str:
    """
    Reads all .txt files from the knowledge/ folder and returns their
    contents as a single string. Since the data is small, we return
    everything instead of doing a vector search.
    
    Args:
        query:  The user's question (ignored in this lightweight version)
        top_k:  Ignored.

    Returns:
        The full text of the knowledge base.
    """
    knowledge_dir = os.path.join(os.path.dirname(__file__), "knowledge")
    full_text = []

    for filename in os.listdir(knowledge_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(knowledge_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    full_text.append(content)

    # Join and return as a single context string
    return "\n\n".join(full_text)
