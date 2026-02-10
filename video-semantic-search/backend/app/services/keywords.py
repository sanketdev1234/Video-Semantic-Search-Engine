from sklearn.feature_extraction.text import TfidfVectorizer

def extract_key_concepts(text, top_k=8):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )
    X = vectorizer.fit_transform([text])
    scores = zip(
        vectorizer.get_feature_names_out(),
        X.toarray()[0]
    )
    keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    return [k for k, _ in keywords[:top_k]]
