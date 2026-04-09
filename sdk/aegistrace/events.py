from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from uuid import UUID


@dataclass
class WorkflowStartEvent:
    workflow_id: str
    metadata: Optional[dict] = None


@dataclass
class WorkflowFinishEvent:
    workflow_run_id: str
    status: str = "completed"


@dataclass
class NodeStartEvent:
    workflow_run_id: str
    node_id: str
    node_type: str
    input_data: Optional[dict] = None
    order_index: int = 0


@dataclass
class NodeFinishEvent:
    node_run_id: str
    status: str = "completed"
    output_data: Optional[dict] = None


@dataclass
class LLMCallEvent:
    node_run_id: str
    model_name: str = "gemini-1.5-flash"
    provider: str = "gemini"
    prompt_text: Optional[str] = None
    response_text: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    prompt_version_id: Optional[str] = None


@dataclass
class RetrievalEvent:
    node_run_id: str
    query_text: str
    doc_texts: list[str] = field(default_factory=list)
    num_docs_retrieved: Optional[int] = None


@dataclass
class ToolCallEvent:
    node_run_id: str
    tool_name: str
    tool_input: Optional[dict] = None
    tool_output: Optional[dict] = None
    latency_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
