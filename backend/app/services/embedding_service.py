"""Embeddings — lazy-load sentence-transformers so the API can bind $PORT before heavy imports."""

from __future__ import annotations

from typing import Any

import numpy as np

from app.config import get_settings

_model: Any = None


def _get_model() -> Any:
    global _model
    if _model is None:
        # Import here: torch + sentence_transformers are huge; loading at module import
        # blocks uvicorn from binding before Render's port scan times out.
        from sentence_transformers import SentenceTransformer

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
    from sklearn.metrics.pairwise import cosine_similarity

    q = np.array(query_embedding).reshape(1, -1)
    d = np.array(doc_embeddings)
    if d.ndim == 1:
        d = d.reshape(1, -1)
    sims = cosine_similarity(q, d)[0]
    return sims.tolist()
