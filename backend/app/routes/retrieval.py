from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.retrieval import RetrievalEvent
from app.models.node import NodeRun
from app.schemas.analytics import RetrievalEventResponse, CoverageOverview

router = APIRouter()


@router.get("/overview", response_model=CoverageOverview)
async def retrieval_overview(db: AsyncSession = Depends(get_db)):
    stmt = select(
        func.avg(RetrievalEvent.coverage_score).label("avg_coverage"),
        func.avg(RetrievalEvent.risk_score).label("avg_risk"),
        func.count().label("total"),
    ).where(RetrievalEvent.coverage_score.isnot(None))

    result = await db.execute(stmt)
    row = result.one()

    low_cov_stmt = select(func.count()).select_from(RetrievalEvent).where(
        RetrievalEvent.coverage_score < 0.5
    )
    low_count = (await db.execute(low_cov_stmt)).scalar() or 0

    return CoverageOverview(
        avg_coverage=round(float(row.avg_coverage or 0), 4),
        avg_risk=round(float(row.avg_risk or 0), 4),
        total_retrievals=row.total or 0,
        low_coverage_count=low_count,
    )


@router.get("/events", response_model=list[RetrievalEventResponse])
async def list_retrieval_events(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(RetrievalEvent)
        .order_by(RetrievalEvent.coverage_score.asc().nulls_last())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    return [
        RetrievalEventResponse(
            id=e.id,
            node_run_id=e.node_run_id,
            query_text=e.query_text,
            num_docs_retrieved=e.num_docs_retrieved,
            doc_texts=e.doc_texts,
            similarity_scores=e.similarity_scores,
            coverage_score=e.coverage_score,
            risk_score=e.risk_score,
        )
        for e in events
    ]


@router.get("/{workflow_run_id}", response_model=list[RetrievalEventResponse])
async def get_workflow_retrievals(workflow_run_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(RetrievalEvent)
        .join(NodeRun, RetrievalEvent.node_run_id == NodeRun.id)
        .where(NodeRun.workflow_run_id == workflow_run_id)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    if not events:
        raise HTTPException(status_code=404, detail="No retrieval events found")
    return [
        RetrievalEventResponse(
            id=e.id,
            node_run_id=e.node_run_id,
            query_text=e.query_text,
            num_docs_retrieved=e.num_docs_retrieved,
            doc_texts=e.doc_texts,
            similarity_scores=e.similarity_scores,
            coverage_score=e.coverage_score,
            risk_score=e.risk_score,
        )
        for e in events
    ]
