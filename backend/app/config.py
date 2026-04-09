import json

from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aegistrace"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/aegistrace"

    @field_validator("database_url", mode="before")
    @classmethod
    def use_asyncpg_for_sqlalchemy_async(cls, v: object) -> object:
        """Neon/Render often provide postgresql:// — SQLAlchemy async needs postgresql+asyncpg://."""
        if isinstance(v, str) and v.startswith("postgresql://") and "+asyncpg" not in v.split("://", 1)[0]:
            return "postgresql+asyncpg://" + v.removeprefix("postgresql://")
        return v

    allowed_origins: list[str] = ["http://localhost:3000", "https://aegistrace-dashboard.vercel.app"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: object) -> list[str]:
        """Accept JSON array or comma-separated origins (Render env is easy to get wrong)."""
        if v is None:
            return ["http://localhost:3000"]
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return ["http://localhost:3000"]
            if s.startswith("["):
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            return [x.strip() for x in s.split(",") if x.strip()]
        return ["http://localhost:3000"]
    embedding_model: str = "all-MiniLM-L6-v2"
    gemini_cost_per_1k_input: float = 0.000125
    gemini_cost_per_1k_output: float = 0.000375

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
