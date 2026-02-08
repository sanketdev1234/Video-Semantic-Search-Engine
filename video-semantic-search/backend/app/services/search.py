from sentence_transformers import SentenceTransformer
from app.services.store import search_embeddings
from app.config import get_settings

settings = get_settings()

# Load embedding model once
embedder = SentenceTransformer(settings.EMBEDDING_MODEL)


def semantic_search(query: str):
    """
    Perform semantic search over stored embeddings
    """
    query_embedding = embedder.encode(query)
    results = search_embeddings(query_embedding, top_k=settings.TOP_K_RESULTS)
    return results
