from sentence_transformers import SentenceTransformer
from app.services.store import search_embeddings
from app.config import get_settings
from typing import Optional

settings = get_settings()

# Load embedding model once (CPU)
embedder = SentenceTransformer(settings.EMBEDDING_MODEL, device="cpu")


def semantic_search(query: str, video_id: Optional[str] = None):
    """
    Perform semantic search over stored embeddings
    Optionally filter by video_id
    """
    query_embedding = embedder.encode(query)
    results = search_embeddings(
        query_embedding, 
        top_k=settings.TOP_K_RESULTS,
        video_id=video_id
    )
    return results
