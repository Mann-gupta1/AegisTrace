from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_call import LLMCall
from app.models.retrieval import RetrievalEvent
from app.models.prompt_version import PromptVersion


async def compare_prompt_versions(db: AsyncSession, v1_id: UUID, v2_id: UUID) -> dict:
    """Compare two prompt versions across latency, confidence, coverage, and token usage."""
    v1 = await db.get(PromptVersion, v1_id)
    v2 = await db.get(PromptVersion, v2_id)

    if not v1 or not v2:
        return {}

    async def _get_metrics(version_id: UUID) -> dict:
        stmt = select(
            func.avg(LLMCall.latency_ms).label("avg_latency"),
            func.avg(LLMCall.confidence_score).label("avg_confidence"),
            func.avg(LLMCall.total_tokens).label("avg_tokens"),
            func.count().label("call_count"),
        ).where(LLMCall.prompt_version_id == version_id)

        result = await db.execute(stmt)
        row = result.one()

        cov_stmt = (
            select(func.avg(RetrievalEvent.coverage_score).label("avg_coverage"))
            .join(LLMCall, LLMCall.node_run_id == RetrievalEvent.node_run_id)
            .where(LLMCall.prompt_version_id == version_id)
        )
        cov_result = await db.execute(cov_stmt)
        cov_row = cov_result.one()

        return {
            "avg_latency": float(row.avg_latency or 0),
            "avg_confidence": float(row.avg_confidence or 0),
            "avg_tokens": float(row.avg_tokens or 0),
            "avg_coverage": float(cov_row.avg_coverage or 0),
        }

    m1 = await _get_metrics(v1_id)
    m2 = await _get_metrics(v2_id)

    return {
        "v1_id": v1_id,
        "v2_id": v2_id,
        "v1_name": v1.prompt_name,
        "v2_name": v2.prompt_name,
        "v1_version": v1.version,
        "v2_version": v2.version,
        "latency_delta_ms": m2["avg_latency"] - m1["avg_latency"],
        "confidence_delta": m2["avg_confidence"] - m1["avg_confidence"],
        "coverage_delta": m2["avg_coverage"] - m1["avg_coverage"],
        "token_delta": int(m2["avg_tokens"] - m1["avg_tokens"]),
        "v1_avg_latency": m1["avg_latency"],
        "v2_avg_latency": m2["avg_latency"],
        "v1_avg_confidence": m1["avg_confidence"],
        "v2_avg_confidence": m2["avg_confidence"],
        "v1_avg_coverage": m1["avg_coverage"],
        "v2_avg_coverage": m2["avg_coverage"],
        "v1_avg_tokens": m1["avg_tokens"],
        "v2_avg_tokens": m2["avg_tokens"],
    }
