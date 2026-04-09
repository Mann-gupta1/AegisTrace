from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aegistrace"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/aegistrace"
    allowed_origins: list[str] = ["http://localhost:3000", "https://aegistrace-dashboard.vercel.app"]
    embedding_model: str = "all-MiniLM-L6-v2"
    gemini_cost_per_1k_input: float = 0.000125
    gemini_cost_per_1k_output: float = 0.000375

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
