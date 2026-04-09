from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
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
