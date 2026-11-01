"""FastAPI dependencies.

Everything a route needs arrives through one of these, so no handler constructs its own
session, client or settings. That is what makes the routes testable: a test overrides one
function and the whole graph follows.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, TypeAlias

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import get_sessionmaker
from app.llm.base import BaseClient


async def db_session() -> AsyncIterator[AsyncSession]:
    """One session per request, closed when the request ends."""
    async with get_sessionmaker()() as session:
        yield session


def settings_dep() -> Settings:
    return get_settings()


def llm_client(request: Request) -> BaseClient:
    """The provider client built once at startup and stored on app.state.

    Not constructed per request: the SDK clients hold connection pools, and rebuilding one
    per request would throw away the pool every time.
    """
    client = getattr(request.app.state, "llm", None)
    if client is None:  # pragma: no cover - lifespan always sets it
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM client not initialised",
        )
    return client


async def require_api_key(
    settings: Annotated[Settings, Depends(settings_dep)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """Enforce the demo key when configured to.

    Disabled by default so a fresh clone's curl examples work. Enabled in the deployed
    environment, because an unauthenticated public endpoint that calls a paid API is a
    bill waiting for a stranger with a loop.
    """
    if not settings.enforce_api_key:
        return
    if x_api_key != settings.demo_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or invalid X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )


SessionDep: TypeAlias = Annotated[AsyncSession, Depends(db_session)]
SettingsDep: TypeAlias = Annotated[Settings, Depends(settings_dep)]
ClientDep: TypeAlias = Annotated[BaseClient, Depends(llm_client)]
