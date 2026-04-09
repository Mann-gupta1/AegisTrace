from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class WorkflowStartEvent(BaseModel):
    workflow_id: str
    metadata: Optional[dict] = None


class WorkflowFinishEvent(BaseModel):
    workflow_run_id: UUID
    status: str = "completed"


class NodeStartEvent(BaseModel):
    workflow_run_id: UUID
    node_id: str
    node_type: str  # retrieval | tool | llm | postprocessing
    input_data: Optional[dict] = None
    order_index: int = 0


class NodeFinishEvent(BaseModel):
    node_run_id: UUID
    status: str = "completed"
    output_data: Optional[dict] = None


class LLMCallEvent(BaseModel):
    node_run_id: UUID
    model_name: str = "gemini-1.5-flash"
    provider: str = "gemini"
    prompt_text: Optional[str] = None
    response_text: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    prompt_version_id: Optional[UUID] = None


class RetrievalEventCreate(BaseModel):
    node_run_id: UUID
    query_text: str
    doc_texts: list[str] = Field(default_factory=list)
    num_docs_retrieved: Optional[int] = None


class ToolCallEvent(BaseModel):
    node_run_id: UUID
    tool_name: str
    tool_input: Optional[dict] = None
    tool_output: Optional[dict] = None
    latency_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
