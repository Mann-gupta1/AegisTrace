from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.workflow import WorkflowRun
from app.models.node import NodeRun
from app.models.llm_call import LLMCall
from app.models.token_usage import TokenUsage
from app.services.token_analyzer import get_token_aggregation
from app.services.metrics_engine import compute_latency_percentiles
from app.schemas.analytics import TokenAggregation, LatencyPercentiles, ConfidenceBucket

router = APIRouter()


@router.get("/tokens", response_model=list[TokenAggregation])
async def token_analytics(
    group_by: str = Query(default="model", enum=["model", "workflow", "node"]),
    db: AsyncSession = Depends(get_db),
):
    rows = await get_token_aggregation(db, group_by)
    return rows


@router.get("/latency", response_model=list[LatencyPercentiles])
async def latency_analytics(db: AsyncSession = Depends(get_db)):
    stmt = select(
        cast(WorkflowRun.start_time, Date).label("date"),
        func.array_agg(WorkflowRun.total_latency_ms).label("latencies"),
    ).where(
        WorkflowRun.total_latency_ms.isnot(None)
    ).group_by(
        cast(WorkflowRun.start_time, Date)
    ).order_by(
        cast(WorkflowRun.start_time, Date)
    )

    result = await db.execute(stmt)
    rows = result.all()

    output = []
    for row in rows:
        percs = compute_latency_percentiles(row.latencies)
        output.append(
            LatencyPercentiles(
                date=str(row.date),
                p50=percs["p50"],
                p95=percs["p95"],
                p99=percs["p99"],
            )
        )
    return output


@router.get("/confidence", response_model=list[ConfidenceBucket])
async def confidence_analytics(db: AsyncSession = Depends(get_db)):
    stmt = select(LLMCall.confidence_score).where(LLMCall.confidence_score.isnot(None))
    result = await db.execute(stmt)
    scores = [r[0] for r in result.all()]

    buckets = {
        "0.0-0.2": 0,
        "0.2-0.4": 0,
        "0.4-0.6": 0,
        "0.6-0.8": 0,
        "0.8-1.0": 0,
    }
    for s in scores:
        if s < 0.2:
            buckets["0.0-0.2"] += 1
        elif s < 0.4:
            buckets["0.2-0.4"] += 1
        elif s < 0.6:
            buckets["0.4-0.6"] += 1
        elif s < 0.8:
            buckets["0.6-0.8"] += 1
        else:
            buckets["0.8-1.0"] += 1

    return [ConfidenceBucket(bucket=k, count=v) for k, v in buckets.items()]
