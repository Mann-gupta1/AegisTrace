# AegisTrace — Agent Observability Platform

Trace, evaluate, and debug multi-step agent pipelines in production environments.

## Architecture

```
Weave Runtime → Trace SDK → Collector API (FastAPI) → PostgreSQL + pgvector → Metrics Engine → Next.js Dashboard
```

## Features

- **Execution Tracing** — Capture prompt, retrieval docs, tool calls, response, latency, confidence, and token usage
- **Retrieval Coverage Scoring** — Compute query vs. retrieved context similarity with coverage % and risk score
- **Token Usage Analytics** — Track tokens per workflow, node, and model with cost estimation
- **Prompt Version Comparison** — Compare accuracy, latency, coverage, and confidence across prompt versions
- **Execution Timeline Viewer** — Waterfall visualization of retrieval, tool, model, and postprocessing steps
- **Hallucination Risk Estimation** — Combined signal from low coverage, output novelty, and tool failure ratio

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI, SQLAlchemy, Pydantic v2 |
| Database | PostgreSQL + pgvector |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| SDK | Python (httpx) |
| Deployment | Render, Vercel, Railway |

## Quick Start (Local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL with pgvector extension

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run migrations
alembic upgrade head

# Seed demo data
python seed.py

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000

### Docker Compose

```bash
docker compose up
```

## Trace SDK Usage

```python
from aegistrace import AegisTrace

tracer = AegisTrace(collector_url="http://localhost:8000")

async with tracer.workflow("my_pipeline") as wf:
    async with wf.node("retriever", node_type="retrieval") as node:
        docs = await retrieve(query)
        await node.log_retrieval(query=query, docs=docs)

    async with wf.node("gemini", node_type="llm") as node:
        result = await call_gemini(query, docs)
        await node.log_llm_call(
            model="gemini-1.5-flash",
            prompt=query,
            response=result.text,
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            confidence=result.confidence,
        )
```

## Production Deployment

| Service | Platform | URL Pattern |
|---------|----------|-------------|
| Database | Railway | PostgreSQL with `CREATE EXTENSION vector;` |
| Backend | Render | `uvicorn app.main:app --host 0.0.0.0 --port 10000` |
| Frontend | Vercel | Auto-deploy from `frontend/` directory |

### Environment Variables

**Backend (Render):**
- `DATABASE_URL` — Railway PostgreSQL connection string (asyncpg format)
- `ALLOWED_ORIGINS` — JSON array of allowed frontend origins
- `EMBEDDING_MODEL` — Sentence transformer model name

**Frontend (Vercel):**
- `NEXT_PUBLIC_API_URL` — Backend API URL on Render

## API Endpoints

### Trace Collection
- `POST /trace/workflow-start` — Start workflow run
- `POST /trace/node-start` — Start node execution
- `POST /trace/llm-call` — Log LLM invocation
- `POST /trace/retrieval` — Log retrieval with coverage scoring
- `POST /trace/tool-call` — Log tool execution
- `POST /trace/node-finish` — Complete node execution
- `POST /trace/workflow-finish` — Finalize workflow

### Query & Analytics
- `GET /runs` — List workflow runs
- `GET /runs/{id}` — Workflow detail with all events
- `GET /runs/{id}/timeline` — Execution timeline
- `GET /analytics/tokens` — Token usage aggregation
- `GET /analytics/latency` — Latency percentiles
- `GET /analytics/confidence` — Confidence distribution
- `GET /retrieval-quality/overview` — Coverage overview
- `GET /prompts` — Prompt version registry
- `GET /prompts/compare` — Prompt version comparison
