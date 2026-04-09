import httpx
import time
from dataclasses import asdict
from typing import Optional

from aegistrace.events import (
    WorkflowStartEvent,
    WorkflowFinishEvent,
    NodeStartEvent,
    NodeFinishEvent,
    LLMCallEvent,
    RetrievalEvent,
    ToolCallEvent,
)
from aegistrace.context import WorkflowContext, NodeContext


class AegisTrace:
    """Client for sending trace events to the AegisTrace Collector API."""

    def __init__(self, collector_url: str = "http://localhost:8000", timeout: float = 10.0):
        self._base_url = collector_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=timeout)
        self._sync_client = httpx.Client(base_url=self._base_url, timeout=timeout)

    async def _post(self, path: str, data: dict) -> dict:
        resp = await self._client.post(path, json=data)
        resp.raise_for_status()
        return resp.json()

    def _post_sync(self, path: str, data: dict) -> dict:
        resp = self._sync_client.post(path, json=data)
        resp.raise_for_status()
        return resp.json()

    async def trace_workflow_start(self, workflow_id: str, metadata: Optional[dict] = None) -> str:
        event = WorkflowStartEvent(workflow_id=workflow_id, metadata=metadata)
        result = await self._post("/trace/workflow-start", asdict(event))
        return result["workflow_run_id"]

    async def trace_workflow_finish(self, workflow_run_id: str, status: str = "completed") -> dict:
        event = WorkflowFinishEvent(workflow_run_id=workflow_run_id, status=status)
        return await self._post("/trace/workflow-finish", asdict(event))

    async def trace_node_start(
        self, workflow_run_id: str, node_id: str, node_type: str,
        input_data: Optional[dict] = None, order_index: int = 0,
    ) -> str:
        event = NodeStartEvent(
            workflow_run_id=workflow_run_id, node_id=node_id,
            node_type=node_type, input_data=input_data, order_index=order_index,
        )
        result = await self._post("/trace/node-start", asdict(event))
        return result["node_run_id"]

    async def trace_node_finish(
        self, node_run_id: str, status: str = "completed", output_data: Optional[dict] = None,
    ) -> dict:
        event = NodeFinishEvent(node_run_id=node_run_id, status=status, output_data=output_data)
        return await self._post("/trace/node-finish", asdict(event))

    async def log_llm_call(
        self, node_run_id: str, model: str = "gemini-1.5-flash", provider: str = "gemini",
        prompt: Optional[str] = None, response: Optional[str] = None,
        prompt_tokens: int = 0, completion_tokens: int = 0,
        latency_ms: Optional[float] = None, confidence: Optional[float] = None,
        prompt_version_id: Optional[str] = None,
    ) -> dict:
        event = LLMCallEvent(
            node_run_id=node_run_id, model_name=model, provider=provider,
            prompt_text=prompt, response_text=response,
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms, confidence_score=confidence,
            prompt_version_id=prompt_version_id,
        )
        return await self._post("/trace/llm-call", asdict(event))

    async def log_retrieval(
        self, node_run_id: str, query: str, docs: list[str],
    ) -> dict:
        event = RetrievalEvent(
            node_run_id=node_run_id, query_text=query,
            doc_texts=docs, num_docs_retrieved=len(docs),
        )
        return await self._post("/trace/retrieval", asdict(event))

    async def log_tool_call(
        self, node_run_id: str, tool_name: str,
        tool_input: Optional[dict] = None, tool_output: Optional[dict] = None,
        latency_ms: Optional[float] = None, success: bool = True,
        error_message: Optional[str] = None,
    ) -> dict:
        event = ToolCallEvent(
            node_run_id=node_run_id, tool_name=tool_name,
            tool_input=tool_input, tool_output=tool_output,
            latency_ms=latency_ms, success=success, error_message=error_message,
        )
        return await self._post("/trace/tool-call", asdict(event))

    def workflow(self, workflow_id: str, metadata: Optional[dict] = None) -> "WorkflowContext":
        return WorkflowContext(self, workflow_id, metadata)

    async def close(self):
        await self._client.aclose()
        self._sync_client.close()
