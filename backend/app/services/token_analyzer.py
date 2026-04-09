from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token_usage import TokenUsage
from app.config import get_settings

PRICING = {
    "gemini-1.5-flash": {"input": 0.000125, "output": 0.000375},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
}


def estimate_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    prices = PRICING.get(model_name, {"input": 0.0001, "output": 0.0004})
    cost = (prompt_tokens / 1000 * prices["input"]) + (completion_tokens / 1000 * prices["output"])
    return round(cost, 8)


async def get_token_aggregation(db: AsyncSession, group_by: str = "model") -> list[dict]:
    """Aggregate token usage by model, workflow, or node."""
    if group_by == "workflow":
        group_col = TokenUsage.workflow_run_id
    elif group_by == "node":
        group_col = TokenUsage.node_run_id
    else:
        group_col = TokenUsage.model_name

    stmt = (
        select(
            group_col.label("group_key"),
            func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
            func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost_usd).label("estimated_cost_usd"),
            func.count().label("count"),
        )
        .group_by(group_col)
        .order_by(func.sum(TokenUsage.total_tokens).desc())
    )

    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "group_key": str(r.group_key),
            "prompt_tokens": r.prompt_tokens or 0,
            "completion_tokens": r.completion_tokens or 0,
            "total_tokens": r.total_tokens or 0,
            "estimated_cost_usd": float(r.estimated_cost_usd or 0),
            "count": r.count,
        }
        for r in rows
    ]
