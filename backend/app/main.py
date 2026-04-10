from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import get_settings
from app.database import async_session
from app.routes import traces, runs, analytics, prompts, retrieval

settings = get_settings()

app = FastAPI(
    title="AegisTrace",
    description="Observability Platform for LLM Workflows",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(traces.router, prefix="/trace", tags=["Trace Collection"])
app.include_router(runs.router, prefix="/runs", tags=["Workflow Runs"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(prompts.router, prefix="/prompts", tags=["Prompt Versions"])
app.include_router(retrieval.router, prefix="/retrieval-quality", tags=["Retrieval Quality"])


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "aegistrace-collector"}


@app.get("/health/db")
async def health_db():
    """Checks DB connectivity and that Alembic tables exist (SELECT 1 alone is not enough)."""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            r = await session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'workflow_runs')"
                )
            )
            has_workflow_runs = bool(r.scalar())
        body = {
            "status": "ok",
            "database": "reachable",
            "workflow_runs_table": has_workflow_runs,
        }
        if not has_workflow_runs:
            body["hint"] = "Run migrations: alembic upgrade head (Render build command)"
        return body
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "unreachable",
                "error_type": type(exc).__name__,
            },
        )
