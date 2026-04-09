import numpy as np
from app.services.embedding_service import encode_text, encode_texts, compute_similarity


def compute_coverage(query: str, docs: list[str]) -> tuple[float, float, list[float], list[float], list[list[float]]]:
    """Compute retrieval coverage score and risk score.

    Returns (coverage_score, risk_score, similarity_scores, query_embedding, doc_embeddings)
    """
    if not docs:
        return 0.0, 1.0, [], encode_text(query), []

    q_emb = encode_text(query)
    d_embs = encode_texts(docs)
    sims = compute_similarity(q_emb, d_embs)

    coverage = float(np.mean(sims))
    risk = float(1.0 - coverage)

    return coverage, risk, sims, q_emb, d_embs


def compute_hallucination_risk(
    coverage_score: float,
    response_text: str | None = None,
    doc_texts: list[str] | None = None,
    tool_failure_ratio: float = 0.0,
) -> float:
    """Estimate hallucination risk from coverage, novelty, and tool reliability."""
    base_risk = 1.0 - coverage_score

    novelty_score = 0.0
    if response_text and doc_texts:
        resp_emb = encode_text(response_text)
        doc_embs = encode_texts(doc_texts)
        sims = compute_similarity(resp_emb, doc_embs)
        novelty_score = float(1.0 - np.mean(sims)) if sims else 0.5

    risk = (base_risk * 0.4) + (novelty_score * 0.4) + (tool_failure_ratio * 0.2)
    return min(max(risk, 0.0), 1.0)


def compute_latency_percentiles(latencies: list[float]) -> dict[str, float]:
    """Compute p50, p95, p99 latency percentiles."""
    if not latencies:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
    arr = np.array(latencies)
    return {
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
    }
