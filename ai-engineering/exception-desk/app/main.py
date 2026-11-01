"""FastAPI application.

The lifespan builds the provider client once and disposes the database pool on shutdown —
the two things that must not happen per request.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app import __version__
from app.api import exceptions as exceptions_router
from app.api import ops as ops_router
from app.config import get_settings
from app.db.session import dispose_engine
from app.llm import make_client
from app.llm.base import BaseClient

logger = logging.getLogger(__name__)

UI_DIR = Path(__file__).resolve().parent.parent / "ui"

DESCRIPTION = """
An LLM-backed triage service for supply-chain exceptions.

Inbound supplier emails and planner notes go in; validated, evidence-backed records with a
recommended action come out. Every record carries the tool results that supported it, the
prompt version that produced it, and what it cost.

**The model recommends. A human decides.**
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    # Built once. The SDK clients hold connection pools; rebuilding per request would
    # discard the pool every time.
    client: BaseClient = make_client(settings=settings)
    app.state.llm = client
    app.state.settings = settings
    logger.info(
        "exception-desk %s starting | provider=%s model=%s prompt_version=%s",
        __version__,
        client.provider,
        client.model,
        settings.prompt_version,
    )
    if client.provider == "mock":
        logger.warning(
            "LLM_PROVIDER=mock — triage runs offline against deterministic stand-ins. "
            "Set LLM_PROVIDER=anthropic|openai|ollama for real calls."
        )

    try:
        yield
    finally:
        await dispose_engine()
        logger.info("exception-desk shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="exception-desk",
        description=DESCRIPTION,
        version=__version__,
        lifespan=lifespan,
    )

    # Open so the single static UI page can call the API from anywhere. Narrow this to the
    # deployed origin before going public.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.include_router(ops_router.router)
    app.include_router(exceptions_router.router)

    # Served from the same origin as the API so the page needs no CORS dance and no build
    # step. `include_in_schema=False` keeps it out of the API docs.
    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(UI_DIR / "index.html")

    if settings.enforce_api_key:
        logger.info("X-API-Key enforcement is ON")
    else:
        logger.warning(
            "X-API-Key enforcement is OFF (ENFORCE_API_KEY=false). "
            "Enable it before exposing this service publicly."
        )

    return app


app = create_app()
