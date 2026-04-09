import os
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


def get_database_url() -> str:
    """Sync URL for Alembic (psycopg2). Prefer DATABASE_URL_SYNC; else strip +asyncpg from DATABASE_URL."""
    sync_url = os.environ.get("DATABASE_URL_SYNC")
    if sync_url:
        return sync_url
    async_url = os.environ.get("DATABASE_URL", "")
    if async_url.startswith("postgresql+asyncpg://"):
        return async_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if async_url.startswith("postgresql://"):
        return async_url
    return config.get_main_option("sqlalchemy.url") or ""


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
