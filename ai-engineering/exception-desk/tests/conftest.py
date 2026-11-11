"""Test fixtures.

The environment is set *before* any app module is imported, because ``get_settings`` is
cached and ``app.db.session`` builds its engine from it. A test database is used so the
suite never touches development data.

The schema is created by running the real Alembic migration rather than
``metadata.create_all()`` — so the tests verify the migration, not just the models. That
distinction is the whole reason migrations exist.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest

TEST_DATABASE_URL = (
    "postgresql+asyncpg://exception_desk:exception_desk@localhost:5432/exception_desk_test"
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["LLM_PROVIDER"] = "mock"
os.environ["PROMPT_VERSION"] = "v1"

from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.db.session import get_engine, get_sessionmaker  # noqa: E402
from app.main import create_app  # noqa: E402

TABLES = "exceptions, exception_evidence, decisions, llm_calls, ingest_jobs"


@pytest.fixture(scope="session")
def migrated_schema() -> None:
    """Run `alembic upgrade head` against the test database, once per session."""
    from alembic import command
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "app/db/migrations")
    command.upgrade(cfg, "head")


@pytest.fixture
async def clean_tables(migrated_schema: None) -> AsyncIterator[None]:
    """Empty every table around each test.

    Deliberately *not* autouse: an async fixture cannot serve a synchronous test, and most
    of the suite is pure unit tests that never touch the database. Only ``client`` pulls
    this in.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))
    yield
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def session(clean_tables: None) -> AsyncIterator[AsyncSession]:
    """A raw session, for tests that exercise the data layer without going through HTTP."""
    async with get_sessionmaker()() as s:
        yield s


@pytest.fixture
async def client(clean_tables: None) -> AsyncIterator[AsyncClient]:
    """An in-process HTTP client — no server, no port, real routing and lifespan."""
    app = create_app()
    transport = ASGITransport(app=app)
    # The lifespan must start before the client is used, so app.state.llm exists.
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=transport, base_url="http://test") as ac,
    ):
        yield ac
