import faiss
import numpy as np
from typing import List, Dict, Optional
import pickle
import os
from app.config import get_settings

settings = get_settings()

# Embedding dimensions
TEXT_DIM = 384     # SentenceTransformer (all-MiniLM-L6-v2)
VISUAL_DIM = 512   # CLIP ViT-B/32

# FAISS Indexes
text_index = faiss.IndexFlatL2(TEXT_DIM)
visual_index = faiss.IndexFlatL2(VISUAL_DIM)

# Metadata Stores
text_metadata: List[Dict] = []
visual_metadata: List[Dict] = []

# Video metadata
video_metadata: Dict[str, Dict] = {}


def save_indexes():
    """Save FAISS indexes and metadata to disk"""
    os.makedirs(settings.INDEX_DIR, exist_ok=True)
    
    # Save FAISS indexes
    faiss.write_index(text_index, os.path.join(settings.INDEX_DIR, "text_index.faiss"))
    faiss.write_index(visual_index, os.path.join(settings.INDEX_DIR, "visual_index.faiss"))
    
    # Save metadata
    with open(os.path.join(settings.INDEX_DIR, "text_metadata.pkl"), "wb") as f:
        pickle.dump(text_metadata, f)
    
    with open(os.path.join(settings.INDEX_DIR, "visual_metadata.pkl"), "wb") as f:
        pickle.dump(visual_metadata, f)
    
    with open(os.path.join(settings.INDEX_DIR, "video_metadata.pkl"), "wb") as f:
        pickle.dump(video_metadata, f)
    
    print(f"✅ Indexes saved: {text_index.ntotal} text, {visual_index.ntotal} visual")


def load_indexes():
    """Load FAISS indexes and metadata from disk"""
    global text_index, visual_index, text_metadata, visual_metadata, video_metadata
    
    text_index_path = os.path.join(settings.INDEX_DIR, "text_index.faiss")
    visual_index_path = os.path.join(settings.INDEX_DIR, "visual_index.faiss")
    
    if os.path.exists(text_index_path):
        text_index = faiss.read_index(text_index_path)
        print(f"✅ Loaded text index: {text_index.ntotal} embeddings")
    
    if os.path.exists(visual_index_path):
        visual_index = faiss.read_index(visual_index_path)
        print(f"✅ Loaded visual index: {visual_index.ntotal} embeddings")
    
    # Load metadata
    text_meta_path = os.path.join(settings.INDEX_DIR, "text_metadata.pkl")
    if os.path.exists(text_meta_path):
        with open(text_meta_path, "rb") as f:
            text_metadata = pickle.load(f)
    
    visual_meta_path = os.path.join(settings.INDEX_DIR, "visual_metadata.pkl")
    if os.path.exists(visual_meta_path):
        with open(visual_meta_path, "rb") as f:
            visual_metadata = pickle.load(f)
    
    video_meta_path = os.path.join(settings.INDEX_DIR, "video_metadata.pkl")
    if os.path.exists(video_meta_path):
        with open(video_meta_path, "rb") as f:
            video_metadata = pickle.load(f)


def add_video_metadata(video_id: str, filename: str, source: str, url: Optional[str] = None):
    """Store video metadata"""
    video_metadata[video_id] = {
        "video_id": video_id,
        "filename": filename,
        "source": source,
        "url": url
    }
    save_indexes()


def add_embedding(
    video_id: str,
    embedding,
    timestamp: float,
    text: str,
    modality: str = "text"
):
    """Store embedding + metadata into correct FAISS index"""
    
    vec = np.array(embedding, dtype="float32")
    
    # Ensure correct shape (1, dim)
    if vec.ndim == 1:
        vec = np.expand_dims(vec, axis=0)
    
    if modality == "visual":
        if vec.shape[1] != VISUAL_DIM:
            raise ValueError(
                f"Visual embedding dim mismatch: {vec.shape[1]} != {VISUAL_DIM}"
            )
        
        visual_index.add(vec)
        visual_metadata.append({
            "video_id": video_id,
            "timestamp": timestamp,
            "text": text,
            "source": video_metadata.get(video_id, {}).get("source", "upload")
        })
    
    else:  # TEXT (default)
        if vec.shape[1] != TEXT_DIM:
            raise ValueError(
                f"Text embedding dim mismatch: {vec.shape[1]} != {TEXT_DIM}"
            )
        
        text_index.add(vec)
        text_metadata.append({
            "video_id": video_id,
            "timestamp": timestamp,
            "text": text,
            "source": video_metadata.get(video_id, {}).get("source", "upload")
        })
    
    # Save after adding embeddings
    if text_index.ntotal % 50 == 0 or visual_index.ntotal % 50 == 0:
        save_indexes()


def search_embeddings(
    query_embedding: np.ndarray,
    top_k: int = 5,
    video_id: Optional[str] = None
):
    """Semantic search over TEXT embeddings with optional video filtering"""
    
    if text_index.ntotal == 0:
        print("❌ No text embeddings indexed yet")
        return []
    
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    
    query_embedding = query_embedding.astype("float32")
    
    # Search more results if filtering by video
    search_k = top_k * 10 if video_id else top_k
    distances, indices = text_index.search(query_embedding, min(search_k, text_index.ntotal))
    
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx == -1:
            continue
        
        meta = text_metadata[idx]
        
        # Filter by video_id if provided
        if video_id and meta["video_id"] != video_id:
            continue
        
        # Get video metadata for deep link
        video_meta = video_metadata.get(meta["video_id"], {})
        deep_link = None
        
        if video_meta.get("source") == "url" and video_meta.get("url"):
            deep_link = build_youtube_link(video_meta["url"], meta["timestamp"])
        
        results.append({
            "video_id": meta["video_id"],
            "timestamp": meta["timestamp"],
            "text": meta["text"],
            "score": float(dist),
            "source": meta["source"],
            "deep_link": deep_link
        })
        
        if len(results) >= top_k:
            break
    
    return results


def build_youtube_link(url: str, timestamp: float) -> str:
    """Build YouTube deep link with timestamp"""
    import urllib.parse
    
    # Parse existing URL
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    
    # Add timestamp parameter
    params['t'] = [str(int(timestamp))]
    
    # Rebuild URL
    new_query = urllib.parse.urlencode(params, doseq=True)
    new_url = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return new_url


def get_video_metadata(video_id: str) -> Optional[Dict]:
    """Get metadata for a specific video"""
    return video_metadata.get(video_id)


def stats():
    """Get index statistics"""
    return {
        "text_index_size": text_index.ntotal,
        "visual_index_size": visual_index.ntotal,
        "total_videos": len(video_metadata)
    }
