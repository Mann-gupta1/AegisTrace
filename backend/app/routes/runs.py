from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.workflow import WorkflowRun
from app.models.node import NodeRun
from app.models.llm_call import LLMCall
from app.models.retrieval import RetrievalEvent
from app.models.tool_call import ToolCall
from app.schemas.analytics import (
    WorkflowRunResponse,
    RunDetailResponse,
    NodeRunResponse,
    LLMCallResponse,
    RetrievalEventResponse,
    ToolCallResponse,
    TimelineEntry,
)

router = APIRouter()


@router.get("", response_model=list[WorkflowRunResponse])
async def list_runs(
    status: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(WorkflowRun).order_by(desc(WorkflowRun.start_time)).limit(limit).offset(offset)
    if status:
        stmt = stmt.where(WorkflowRun.status == status)
    result = await db.execute(stmt)
    runs = result.scalars().all()
    return [
        WorkflowRunResponse(
            id=r.id,
            workflow_id=r.workflow_id,
            status=r.status,
            start_time=r.start_time,
            end_time=r.end_time,
            total_latency_ms=r.total_latency_ms,
            total_tokens=r.total_tokens,
            avg_confidence=r.avg_confidence,
            metadata=r.metadata_,
        )
        for r in runs
    ]


@router.get("/summary")
async def runs_summary(db: AsyncSession = Depends(get_db)):
    total_stmt = select(func.count()).select_from(WorkflowRun)
    total = (await db.execute(total_stmt)).scalar() or 0

    active_stmt = select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "running")
    active = (await db.execute(active_stmt)).scalar() or 0

    avg_lat_stmt = select(func.avg(WorkflowRun.total_latency_ms)).where(WorkflowRun.total_latency_ms.isnot(None))
    avg_latency = (await db.execute(avg_lat_stmt)).scalar() or 0

    avg_conf_stmt = select(func.avg(WorkflowRun.avg_confidence)).where(WorkflowRun.avg_confidence.isnot(None))
    avg_confidence = (await db.execute(avg_conf_stmt)).scalar() or 0

    total_tok_stmt = select(func.sum(WorkflowRun.total_tokens))
    total_tokens = (await db.execute(total_tok_stmt)).scalar() or 0

    return {
        "total_runs": total,
        "active_runs": active,
        "avg_latency_ms": round(float(avg_latency), 2),
        "avg_confidence": round(float(avg_confidence), 4),
        "total_tokens": total_tokens,
    }


@router.get("/{run_id}", response_model=RunDetailResponse)
async def get_run_detail(run_id: UUID, db: AsyncSession = Depends(get_db)):
    wf = await db.get(WorkflowRun, run_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    nodes_stmt = select(NodeRun).where(NodeRun.workflow_run_id == run_id).order_by(NodeRun.order_index)
    nodes = (await db.execute(nodes_stmt)).scalars().all()

    node_ids = [n.id for n in nodes]

    llm_stmt = select(LLMCall).where(LLMCall.node_run_id.in_(node_ids)).order_by(LLMCall.timestamp)
    llm_calls = (await db.execute(llm_stmt)).scalars().all()

    ret_stmt = select(RetrievalEvent).where(RetrievalEvent.node_run_id.in_(node_ids))
    retrievals = (await db.execute(ret_stmt)).scalars().all()

    tc_stmt = select(ToolCall).where(ToolCall.node_run_id.in_(node_ids))
    tool_calls = (await db.execute(tc_stmt)).scalars().all()

    return RunDetailResponse(
        workflow=WorkflowRunResponse(
            id=wf.id,
            workflow_id=wf.workflow_id,
            status=wf.status,
            start_time=wf.start_time,
            end_time=wf.end_time,
            total_latency_ms=wf.total_latency_ms,
            total_tokens=wf.total_tokens,
            avg_confidence=wf.avg_confidence,
            metadata=wf.metadata_,
        ),
        nodes=[NodeRunResponse.model_validate(n) for n in nodes],
        llm_calls=[LLMCallResponse.model_validate(c) for c in llm_calls],
        retrieval_events=[
            RetrievalEventResponse(
                id=r.id,
                node_run_id=r.node_run_id,
                query_text=r.query_text,
                num_docs_retrieved=r.num_docs_retrieved,
                doc_texts=r.doc_texts,
                similarity_scores=r.similarity_scores,
                coverage_score=r.coverage_score,
                risk_score=r.risk_score,
            )
            for r in retrievals
        ],
        tool_calls=[ToolCallResponse.model_validate(tc) for tc in tool_calls],
    )


@router.get("/{run_id}/timeline", response_model=list[TimelineEntry])
async def get_run_timeline(run_id: UUID, db: AsyncSession = Depends(get_db)):
    wf = await db.get(WorkflowRun, run_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    nodes_stmt = select(NodeRun).where(NodeRun.workflow_run_id == run_id).order_by(NodeRun.order_index)
    nodes = (await db.execute(nodes_stmt)).scalars().all()

    return [
        TimelineEntry(
            node_id=n.node_id,
            node_type=n.node_type,
            start_time=n.start_time,
            end_time=n.end_time,
            latency_ms=n.latency_ms,
            status=n.status,
            order_index=n.order_index,
        )
        for n in nodes
    ]
