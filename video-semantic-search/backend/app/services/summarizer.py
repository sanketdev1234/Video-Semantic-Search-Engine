from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

def summarize(text_or_lines, top_k=5):
    """
    Summarize by extracting top-k sentences using semantic similarity
    text_or_lines: either a string or list of sentences
    """
    if isinstance(text_or_lines, str):
        # Split into sentences
        sentences = [s.strip() for s in text_or_lines.split(". ") if s.strip()]
    else:
        sentences = [s.strip() for s in text_or_lines if s.strip()]
    
    if not sentences:
        return []
    
    # If only one sentence, return it
    if len(sentences) <= top_k:
        return sentences
    
    doc_embedding = model.encode(" ".join(sentences))
    sent_embeddings = model.encode(sentences)

    scores = util.cos_sim(sent_embeddings, doc_embedding)
    ranked = sorted(
        zip(sentences, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [s for s, _ in ranked[:top_k]]
