"""Async engine and session factory.

Created lazily so importing the app does not require a reachable database — the test suite
and ``--help`` both work with Postgres down.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

#: Drivers that can serve SQLAlchemy's async interface. Checked eagerly because a sync URL
#: produces a confusing failure deep inside the first query instead of at startup.
ASYNC_DRIVERS = ("postgresql+asyncpg://", "postgresql+psycopg://", "sqlite+aiosqlite://")

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        url = get_settings().database_url
        if not url.startswith(ASYNC_DRIVERS):
            raise RuntimeError(
                f"DATABASE_URL must use an async driver {ASYNC_DRIVERS}; got {url!r}. "
                "Postgres needs 'postgresql+asyncpg://'."
            )
        _engine = create_async_engine(url, pool_pre_ping=True, future=True)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _sessionmaker


async def dispose_engine() -> None:
    """Close the pool. Called from the app's lifespan on shutdown."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _sessionmaker = None
