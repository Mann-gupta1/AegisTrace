from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.workflow import WorkflowRun
from app.models.node import NodeRun
from app.models.llm_call import LLMCall
from app.models.retrieval import RetrievalEvent
from app.models.tool_call import ToolCall
from app.models.token_usage import TokenUsage
from app.schemas.trace_events import (
    WorkflowStartEvent,
    WorkflowFinishEvent,
    NodeStartEvent,
    NodeFinishEvent,
    LLMCallEvent,
    RetrievalEventCreate,
    ToolCallEvent,
)
from app.services.metrics_engine import compute_coverage
from app.services.token_analyzer import estimate_cost

router = APIRouter()


@router.post("/workflow-start")
async def workflow_start(event: WorkflowStartEvent, db: AsyncSession = Depends(get_db)):
    run = WorkflowRun(
        workflow_id=event.workflow_id,
        status="running",
        start_time=datetime.now(timezone.utc),
        metadata_=event.metadata,
    )
    db.add(run)
    await db.flush()
    return {"workflow_run_id": str(run.id), "status": "created"}


@router.post("/node-start")
async def node_start(event: NodeStartEvent, db: AsyncSession = Depends(get_db)):
    node = NodeRun(
        workflow_run_id=event.workflow_run_id,
        node_id=event.node_id,
        node_type=event.node_type,
        input_data=event.input_data,
        start_time=datetime.now(timezone.utc),
        status="running",
        order_index=event.order_index,
    )
    db.add(node)
    await db.flush()
    return {"node_run_id": str(node.id), "status": "created"}


@router.post("/llm-call")
async def llm_call(event: LLMCallEvent, db: AsyncSession = Depends(get_db)):
    node = await db.get(NodeRun, event.node_run_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node run not found")

    call = LLMCall(
        node_run_id=event.node_run_id,
        model_name=event.model_name,
        provider=event.provider,
        prompt_text=event.prompt_text,
        response_text=event.response_text,
        prompt_tokens=event.prompt_tokens,
        completion_tokens=event.completion_tokens,
        total_tokens=event.total_tokens,
        latency_ms=event.latency_ms,
        confidence_score=event.confidence_score,
        prompt_version_id=event.prompt_version_id,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(call)

    cost = estimate_cost(event.model_name, event.prompt_tokens, event.completion_tokens)
    usage = TokenUsage(
        workflow_run_id=node.workflow_run_id,
        node_run_id=event.node_run_id,
        model_name=event.model_name,
        prompt_tokens=event.prompt_tokens,
        completion_tokens=event.completion_tokens,
        total_tokens=event.total_tokens,
        estimated_cost_usd=cost,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(usage)
    await db.flush()

    return {"llm_call_id": str(call.id), "estimated_cost_usd": cost}


@router.post("/retrieval")
async def retrieval_event(event: RetrievalEventCreate, db: AsyncSession = Depends(get_db)):
    num_docs = event.num_docs_retrieved or len(event.doc_texts)

    coverage, risk, sims, q_emb, d_embs = compute_coverage(event.query_text, event.doc_texts)

    ret = RetrievalEvent(
        node_run_id=event.node_run_id,
        query_text=event.query_text,
        query_embedding=q_emb,
        num_docs_retrieved=num_docs,
        doc_texts=event.doc_texts,
        similarity_scores=sims,
        coverage_score=coverage,
        risk_score=risk,
    )
    db.add(ret)
    await db.flush()

    return {
        "retrieval_event_id": str(ret.id),
        "coverage_score": coverage,
        "risk_score": risk,
    }


@router.post("/tool-call")
async def tool_call(event: ToolCallEvent, db: AsyncSession = Depends(get_db)):
    tc = ToolCall(
        node_run_id=event.node_run_id,
        tool_name=event.tool_name,
        tool_input=event.tool_input,
        tool_output=event.tool_output,
        latency_ms=event.latency_ms,
        success=event.success,
        error_message=event.error_message,
    )
    db.add(tc)
    await db.flush()
    return {"tool_call_id": str(tc.id)}


@router.post("/node-finish")
async def node_finish(event: NodeFinishEvent, db: AsyncSession = Depends(get_db)):
    node = await db.get(NodeRun, event.node_run_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node run not found")

    now = datetime.now(timezone.utc)
    node.end_time = now
    node.status = event.status
    node.output_data = event.output_data
    if node.start_time:
        node.latency_ms = (now - node.start_time).total_seconds() * 1000

    return {"node_run_id": str(node.id), "latency_ms": node.latency_ms}


@router.post("/workflow-finish")
async def workflow_finish(event: WorkflowFinishEvent, db: AsyncSession = Depends(get_db)):
    wf = await db.get(WorkflowRun, event.workflow_run_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    now = datetime.now(timezone.utc)
    wf.end_time = now
    wf.status = event.status
    if wf.start_time:
        wf.total_latency_ms = (now - wf.start_time).total_seconds() * 1000

    token_stmt = select(func.sum(TokenUsage.total_tokens)).where(
        TokenUsage.workflow_run_id == wf.id
    )
    result = await db.execute(token_stmt)
    wf.total_tokens = result.scalar() or 0

    conf_stmt = (
        select(func.avg(LLMCall.confidence_score))
        .join(NodeRun, LLMCall.node_run_id == NodeRun.id)
        .where(NodeRun.workflow_run_id == wf.id)
        .where(LLMCall.confidence_score.isnot(None))
    )
    result = await db.execute(conf_stmt)
    wf.avg_confidence = result.scalar()

    return {
        "workflow_run_id": str(wf.id),
        "total_latency_ms": wf.total_latency_ms,
        "total_tokens": wf.total_tokens,
        "avg_confidence": wf.avg_confidence,
    }
