import sys
from logging.config import fileConfig
from pathlib import Path

# Backend root must be on PYTHONPATH so `import app` works (Render, Docker, CI).
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.db_base import Base
from app.models import *  # noqa: F401,F403

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Matches app.config defaults — if .env only sets DATABASE_URL (Neon), Alembic still needs a sync URL.
_DEFAULT_LOCAL_SYNC = "postgresql://postgres:postgres@localhost:5432/aegistrace"


def get_database_url() -> str:
    """Sync URL for Alembic (psycopg2).

    Reads from pydantic Settings so `backend/.env` works. Plain `os.environ` does not
    include .env file keys unless you export them in the shell (which caused localhost fallback).
    """
    from app.config import get_settings

    s = get_settings()

    def to_sync(url: str) -> str:
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url

    sync = to_sync(s.database_url_sync)
    from_async = to_sync(s.database_url)

    if sync != _DEFAULT_LOCAL_SYNC:
        return sync
    # Only DATABASE_URL set (e.g. Neon) — use same host for migrations
    if from_async and from_async != _DEFAULT_LOCAL_SYNC:
        return from_async
    return sync or (config.get_main_option("sqlalchemy.url") or "")


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section, {})
    url = get_database_url()
    if url:
        section = dict(section)
        section["sqlalchemy.url"] = url

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
