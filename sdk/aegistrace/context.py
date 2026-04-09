from __future__ import annotations

import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from aegistrace.client import AegisTrace


class WorkflowContext:
    """Async context manager for tracing a full workflow execution."""

    def __init__(self, tracer: AegisTrace, workflow_id: str, metadata: Optional[dict] = None):
        self._tracer = tracer
        self._workflow_id = workflow_id
        self._metadata = metadata
        self.workflow_run_id: Optional[str] = None
        self._node_counter = 0

    async def __aenter__(self) -> WorkflowContext:
        self.workflow_run_id = await self._tracer.trace_workflow_start(
            self._workflow_id, self._metadata
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        status = "failed" if exc_type else "completed"
        await self._tracer.trace_workflow_finish(self.workflow_run_id, status)
        return False

    def node(self, node_id: str, node_type: str = "llm", input_data: Optional[dict] = None) -> NodeContext:
        order = self._node_counter
        self._node_counter += 1
        return NodeContext(self._tracer, self.workflow_run_id, node_id, node_type, input_data, order)


class NodeContext:
    """Async context manager for tracing a single node execution."""

    def __init__(
        self, tracer: AegisTrace, workflow_run_id: str, node_id: str,
        node_type: str, input_data: Optional[dict], order_index: int,
    ):
        self._tracer = tracer
        self._workflow_run_id = workflow_run_id
        self._node_id = node_id
        self._node_type = node_type
        self._input_data = input_data
        self._order_index = order_index
        self.node_run_id: Optional[str] = None
        self._start_time: float = 0

    async def __aenter__(self) -> NodeContext:
        self._start_time = time.time()
        self.node_run_id = await self._tracer.trace_node_start(
            self._workflow_run_id, self._node_id, self._node_type,
            self._input_data, self._order_index,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        status = "failed" if exc_type else "completed"
        elapsed = (time.time() - self._start_time) * 1000
        await self._tracer.trace_node_finish(
            self.node_run_id, status,
            output_data={"latency_ms": round(elapsed, 2)},
        )
        return False

    async def log_llm_call(self, **kwargs) -> dict:
        return await self._tracer.log_llm_call(node_run_id=self.node_run_id, **kwargs)

    async def log_retrieval(self, query: str, docs: list[str]) -> dict:
        return await self._tracer.log_retrieval(self.node_run_id, query, docs)

    async def log_tool_call(self, **kwargs) -> dict:
        return await self._tracer.log_tool_call(node_run_id=self.node_run_id, **kwargs)
