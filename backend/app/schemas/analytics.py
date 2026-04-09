from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class WorkflowRunResponse(BaseModel):
    id: UUID
    workflow_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_latency_ms: Optional[float] = None
    total_tokens: Optional[int] = None
    avg_confidence: Optional[float] = None
    metadata: Optional[dict] = None

    model_config = {"from_attributes": True}


class NodeRunResponse(BaseModel):
    id: UUID
    workflow_run_id: UUID
    node_id: str
    node_type: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    latency_ms: Optional[float] = None
    status: str
    order_index: int

    model_config = {"from_attributes": True}


class LLMCallResponse(BaseModel):
    id: UUID
    node_run_id: UUID
    model_name: str
    provider: str
    prompt_text: Optional[str] = None
    response_text: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    latency_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    prompt_version_id: Optional[UUID] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class RetrievalEventResponse(BaseModel):
    id: UUID
    node_run_id: UUID
    query_text: Optional[str] = None
    num_docs_retrieved: Optional[int] = None
    doc_texts: Optional[list] = None
    similarity_scores: Optional[list[float]] = None
    coverage_score: Optional[float] = None
    risk_score: Optional[float] = None

    model_config = {"from_attributes": True}


class ToolCallResponse(BaseModel):
    id: UUID
    node_run_id: UUID
    tool_name: str
    tool_input: Optional[dict] = None
    tool_output: Optional[dict] = None
    latency_ms: Optional[float] = None
    success: bool
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class PromptVersionResponse(BaseModel):
    id: UUID
    prompt_name: str
    version: int
    template_text: str
    created_at: datetime
    metadata: Optional[dict] = None

    model_config = {"from_attributes": True}


class PromptVersionCreate(BaseModel):
    prompt_name: str
    version: int
    template_text: str
    metadata: Optional[dict] = None


class TokenUsageResponse(BaseModel):
    id: UUID
    workflow_run_id: UUID
    node_run_id: Optional[UUID] = None
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: Optional[float] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class RunDetailResponse(BaseModel):
    workflow: WorkflowRunResponse
    nodes: list[NodeRunResponse]
    llm_calls: list[LLMCallResponse]
    retrieval_events: list[RetrievalEventResponse]
    tool_calls: list[ToolCallResponse]


class TimelineEntry(BaseModel):
    node_id: str
    node_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    latency_ms: Optional[float] = None
    status: str
    order_index: int


class TokenAggregation(BaseModel):
    group_key: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    count: int


class LatencyPercentiles(BaseModel):
    date: str
    p50: float
    p95: float
    p99: float


class ConfidenceBucket(BaseModel):
    bucket: str
    count: int


class CoverageOverview(BaseModel):
    avg_coverage: float
    avg_risk: float
    total_retrievals: int
    low_coverage_count: int


class PromptComparisonResult(BaseModel):
    v1_id: UUID
    v2_id: UUID
    v1_name: str
    v2_name: str
    v1_version: int
    v2_version: int
    latency_delta_ms: float
    confidence_delta: float
    coverage_delta: float
    token_delta: int
    v1_avg_latency: float
    v2_avg_latency: float
    v1_avg_confidence: float
    v2_avg_confidence: float
    v1_avg_coverage: float
    v2_avg_coverage: float
    v1_avg_tokens: float
    v2_avg_tokens: float
