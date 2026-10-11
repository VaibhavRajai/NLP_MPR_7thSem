import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.core.logging import logger

_model = None
_model_failed = False

def get_sentence_transformer():
    global _model, _model_failed
    if _model is not None:
        return _model
    if _model_failed:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        import os
        # First attempt to load if model is already downloaded locally or fast
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        return _model
    except Exception as e:
        logger.warning(f"SentenceTransformer not loaded or offline ({e}), utilizing TF-IDF semantic representation.")
        _model_failed = True
        return None

class SemanticEncoder:
    def __init__(self):
        self.st_model = get_sentence_transformer()
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=2500,
            ngram_range=(1, 2)
        )

    def encode_sentences(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 0))
            
        if self.st_model is not None:
            try:
                embeddings = self.st_model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
                return np.array(embeddings)
            except Exception as e:
                logger.warning(f"Error computing sentence embeddings with model: {e}")
                
        # TF-IDF fallback vectorization
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        return tfidf_matrix.toarray()

    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        if len(texts) <= 1:
            return np.ones((len(texts), len(texts)))
            
        vectors = self.encode_sentences(texts)
        sim_matrix = cosine_similarity(vectors)
        return sim_matrix
