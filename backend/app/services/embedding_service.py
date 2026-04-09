import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import get_settings

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        settings = get_settings()
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def encode_text(text: str) -> list[float]:
    model = _get_model()
    embedding = model.encode([text])[0]
    return embedding.tolist()


def encode_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    embeddings = model.encode(texts)
    return embeddings.tolist()


def compute_similarity(query_embedding: list[float], doc_embeddings: list[list[float]]) -> list[float]:
    q = np.array(query_embedding).reshape(1, -1)
    d = np.array(doc_embeddings)
    if d.ndim == 1:
        d = d.reshape(1, -1)
    sims = cosine_similarity(q, d)[0]
    return sims.tolist()
