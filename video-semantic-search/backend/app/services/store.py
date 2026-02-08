import faiss
import numpy as np
from typing import List, Dict

# Sentence-transformer embedding size
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2

# FAISS index (L2 distance)
index = faiss.IndexFlatL2(EMBEDDING_DIM)

# Metadata store (same order as FAISS vectors)
metadata_store: List[Dict] = []


def add_embedding(
    video_id: str,
    embedding: np.ndarray,
    timestamp: float,
    text: str
):
    """
    Add a single embedding to FAISS index
    """
    if embedding.ndim == 1:
        embedding = np.expand_dims(embedding, axis=0)

    embedding = embedding.astype("float32")

    index.add(embedding)

    metadata_store.append({
        "video_id": video_id,
        "timestamp": timestamp,
        "text": text,
    })


def search_embeddings(query_embedding: np.ndarray, top_k: int = 5):
    """
    Search FAISS index using query embedding
    """
    if index.ntotal == 0:
        return []

    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)

    query_embedding = query_embedding.astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx == -1:
            continue

        meta = metadata_store[idx]
        results.append({
            "video_id": meta["video_id"],
            "timestamp": meta["timestamp"],
            "text": meta["text"],
            "score": float(dist),
        })

    return results
