from __future__ import annotations

import functools
import asyncio
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from aegistrace.client import AegisTrace


def trace_workflow(tracer: AegisTrace, workflow_id: Optional[str] = None):
    """Decorator to automatically trace a workflow function.

    Usage:
        @trace_workflow(tracer, "my_pipeline")
        async def run_pipeline(query: str):
            ...
    """
    def decorator(func: Callable):
        wf_id = workflow_id or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with tracer.workflow(wf_id) as wf:
                kwargs["_wf_context"] = wf
                return await func(*args, **kwargs)

        return wrapper
    return decorator


def trace_node(tracer: AegisTrace, node_id: Optional[str] = None, node_type: str = "llm"):
    """Decorator to automatically trace a node function.

    The decorated function receives a `_node_context` kwarg with the NodeContext.

    Usage:
        @trace_node(tracer, "retriever", "retrieval")
        async def retrieve_docs(query: str, _node_context=None):
            ...
    """
    def decorator(func: Callable):
        n_id = node_id or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            wf_context = kwargs.pop("_wf_context", None)
            if wf_context is None:
                return await func(*args, **kwargs)

            async with wf_context.node(n_id, node_type) as node:
                kwargs["_node_context"] = node
                return await func(*args, **kwargs)

        return wrapper
    return decorator
