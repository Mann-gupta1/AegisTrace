import ssl
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db_base import Base

__all__ = ["Base", "engine", "async_session", "get_db"]


def _asyncpg_url_and_connect_args(url: str) -> tuple[str, dict]:
    """asyncpg does not accept libpq params like sslmode= or channel_binding= as kwargs."""
    parsed = urlparse(url)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    new_pairs: list[tuple[str, str]] = []
    ssl_required = False
    for key, val in pairs:
        lk = key.lower()
        if lk == "sslmode":
            if val.lower() in ("require", "verify-full", "verify-ca", "prefer", "allow"):
                ssl_required = True
            continue
        if lk == "channel_binding":
            continue
        new_pairs.append((key, val))

    host = (parsed.hostname or "").lower()
    if "neon.tech" in host:
        ssl_required = True

    connect_args: dict = {}
    if ssl_required:
        # True is not always enough on hosted Postgres; default context verifies TLS correctly.
        connect_args["ssl"] = ssl.create_default_context()

    new_query = urlencode(new_pairs)
    cleaned = urlunparse(parsed._replace(query=new_query))
    return cleaned, connect_args


settings = get_settings()
_db_url, _connect_args = _asyncpg_url_and_connect_args(settings.database_url)

engine = create_async_engine(
    _db_url,
    echo=False,
    connect_args=_connect_args,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
