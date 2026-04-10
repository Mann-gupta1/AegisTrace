"""Seed script to generate realistic demo trace data for AegisTrace dashboard."""

import asyncio
import random
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import engine
from app.db_base import Base
from app.models.workflow import WorkflowRun
from app.models.node import NodeRun
from app.models.llm_call import LLMCall
from app.models.retrieval import RetrievalEvent
from app.models.tool_call import ToolCall
from app.models.token_usage import TokenUsage
from app.models.prompt_version import PromptVersion
from app.services.token_analyzer import estimate_cost

WORKFLOW_NAMES = [
    "document_qa_pipeline",
    "customer_support_agent",
    "code_review_assistant",
    "research_summarizer",
    "data_extraction_pipeline",
]

TOOL_NAMES = ["web_search", "calculator", "code_executor", "file_reader", "api_caller"]

SAMPLE_QUERIES = [
    "What are the key benefits of microservice architecture?",
    "Explain the difference between REST and GraphQL APIs",
    "How does garbage collection work in Python?",
    "What are best practices for database indexing?",
    "Describe the CAP theorem in distributed systems",
    "How to implement rate limiting in a web API?",
    "What is the difference between SQL and NoSQL databases?",
    "Explain event-driven architecture patterns",
    "How does OAuth 2.0 authorization flow work?",
    "What are the SOLID principles in software design?",
]

SAMPLE_DOCS = [
    "Microservices enable independent deployment and scaling of services.",
    "REST uses HTTP methods while GraphQL uses a single endpoint with queries.",
    "Python uses reference counting and generational garbage collection.",
    "Database indexes improve query performance by creating B-tree structures.",
    "The CAP theorem states you can only have two of consistency, availability, partition tolerance.",
    "Rate limiting can be implemented using token bucket or sliding window algorithms.",
    "SQL databases are relational while NoSQL supports document, key-value, and graph models.",
    "Event-driven architecture uses events to trigger and communicate between services.",
    "OAuth 2.0 uses authorization codes, access tokens, and refresh tokens.",
    "SOLID principles include Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.",
]

SAMPLE_RESPONSES = [
    "Based on the retrieved context, microservice architecture provides several key benefits including independent scaling...",
    "GraphQL offers more flexibility than REST by allowing clients to request exactly the data they need...",
    "Python's garbage collection mechanism uses a combination of reference counting for immediate cleanup...",
    "Effective database indexing requires understanding query patterns and selecting appropriate index types...",
    "In the context of the CAP theorem, distributed systems must make trade-offs between consistency and availability...",
]

PROMPT_TEMPLATES = [
    ("qa_prompt", "Answer the following question based on the context provided:\n\nContext: {context}\n\nQuestion: {question}"),
    ("qa_prompt", "You are a helpful assistant. Use the following context to answer the question.\n\nContext: {context}\n\nQuestion: {question}\n\nProvide a detailed answer."),
    ("qa_prompt", "Given the context below, provide a comprehensive answer to the question. If the context doesn't contain enough information, state that clearly.\n\nContext: {context}\n\nQuestion: {question}"),
    ("summarizer_prompt", "Summarize the following text:\n\n{text}"),
    ("summarizer_prompt", "Provide a concise summary of the following text, highlighting key points:\n\n{text}"),
]


async def seed_data():
    async_sess = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Short transactions: Neon pooler often drops one long open transaction mid-flight.
    async with async_sess() as db:
        prompt_versions = []
        for i, (name, template) in enumerate(PROMPT_TEMPLATES):
            pv = PromptVersion(
                prompt_name=name,
                version=i + 1,
                template_text=template,
                created_at=datetime.now(timezone.utc) - timedelta(days=30 - i * 5),
                metadata_={"author": "aegistrace-seed"},
            )
            db.add(pv)
            prompt_versions.append(pv)
        await db.flush()
        await db.commit()

    base_time = datetime.now(timezone.utc) - timedelta(days=7)

    for wf_idx in range(25):
        async with async_sess() as db:
            wf_name = random.choice(WORKFLOW_NAMES)
            wf_start = base_time + timedelta(hours=wf_idx * 6, minutes=random.randint(0, 59))
            wf_latency = random.uniform(800, 5000)
            status = random.choices(["completed", "failed"], weights=[0.85, 0.15])[0]

            wf = WorkflowRun(
                workflow_id=wf_name,
                status=status,
                start_time=wf_start,
                end_time=wf_start + timedelta(milliseconds=wf_latency),
                total_latency_ms=wf_latency,
                total_tokens=0,
                avg_confidence=0.0,
                metadata_={"seed": True, "run_index": wf_idx},
            )
            db.add(wf)
            await db.flush()

            node_configs = [
                ("retriever", "retrieval"),
                ("tool_executor", "tool"),
                ("gemini_model", "llm"),
                ("formatter", "postprocessing"),
            ]

            total_tokens = 0
            confidences = []
            current_time = wf_start

            for order, (node_name, node_type) in enumerate(node_configs):
                node_latency = random.uniform(50, 1500)
                node_start = current_time
                node_end = node_start + timedelta(milliseconds=node_latency)
                current_time = node_end + timedelta(milliseconds=random.uniform(5, 50))

                node_status = "completed"
                if status == "failed" and order == len(node_configs) - 1:
                    node_status = "failed"

                node = NodeRun(
                    workflow_run_id=wf.id,
                    node_id=f"{node_name}_{wf_idx}",
                    node_type=node_type,
                    input_data={"query": random.choice(SAMPLE_QUERIES)},
                    output_data={"result": "processed"} if node_status == "completed" else None,
                    start_time=node_start,
                    end_time=node_end,
                    latency_ms=node_latency,
                    status=node_status,
                    order_index=order,
                )
                db.add(node)
                await db.flush()

                if node_type == "retrieval":
                    query = random.choice(SAMPLE_QUERIES)
                    num_docs = random.randint(2, 5)
                    docs = random.sample(SAMPLE_DOCS, min(num_docs, len(SAMPLE_DOCS)))
                    coverage = random.uniform(0.3, 0.95)
                    risk = 1.0 - coverage
                    sims = [random.uniform(coverage - 0.1, coverage + 0.1) for _ in docs]

                    ret = RetrievalEvent(
                        node_run_id=node.id,
                        query_text=query,
                        num_docs_retrieved=num_docs,
                        doc_texts=docs,
                        similarity_scores=sims,
                        coverage_score=round(coverage, 4),
                        risk_score=round(risk, 4),
                    )
                    db.add(ret)

                elif node_type == "tool":
                    tool_name = random.choice(TOOL_NAMES)
                    success = random.random() > 0.1
                    tc = ToolCall(
                        node_run_id=node.id,
                        tool_name=tool_name,
                        tool_input={"action": "execute", "params": {"key": "value"}},
                        tool_output={"result": "success"} if success else None,
                        latency_ms=random.uniform(20, 500),
                        success=success,
                        error_message=None if success else "Tool execution timeout",
                    )
                    db.add(tc)

                elif node_type == "llm":
                    prompt_tokens = random.randint(100, 800)
                    completion_tokens = random.randint(50, 400)
                    tok_total = prompt_tokens + completion_tokens
                    total_tokens += tok_total
                    confidence = random.uniform(0.5, 0.98)
                    confidences.append(confidence)

                    model_name = random.choice(["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"])
                    pv = random.choice(prompt_versions[:3])

                    llm = LLMCall(
                        node_run_id=node.id,
                        model_name=model_name,
                        provider="gemini",
                        prompt_text=random.choice(SAMPLE_QUERIES),
                        response_text=random.choice(SAMPLE_RESPONSES),
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=tok_total,
                        latency_ms=node_latency,
                        confidence_score=round(confidence, 4),
                        prompt_version_id=pv.id,
                        timestamp=node_start,
                    )
                    db.add(llm)

                    cost = estimate_cost(model_name, prompt_tokens, completion_tokens)
                    usage = TokenUsage(
                        workflow_run_id=wf.id,
                        node_run_id=node.id,
                        model_name=model_name,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=tok_total,
                        estimated_cost_usd=cost,
                        timestamp=node_start,
                    )
                    db.add(usage)

            wf.total_tokens = total_tokens
            wf.avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else None

            await db.commit()

    print(
        f"Seeded 25 workflow runs with nodes, LLM calls, retrievals, tool calls, "
        f"and {len(PROMPT_TEMPLATES)} prompt versions."
    )


if __name__ == "__main__":
    asyncio.run(seed_data())
