"""Typed configuration. Every knob the service reads is declared here exactly once.

Nothing else in the codebase touches ``os.environ``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Provider = Literal["mock", "anthropic", "openai", "ollama"]

PACKAGE_ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = PACKAGE_ROOT / "domain" / "prompts"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # -- database ----------------------------------------------------------
    database_url: str = (
        "postgresql+asyncpg://exception_desk:exception_desk@localhost:5432/exception_desk"
    )

    # -- llm ---------------------------------------------------------------
    # `mock` is the default on purpose: the test suite and CI must never spend money,
    # and a developer cloning the repo should get a working service with no keys.
    llm_provider: Provider = "mock"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"

    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-terra"

    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen3:8b"

    request_timeout_s: float = 60.0

    # -- pipeline ----------------------------------------------------------
    prompt_version: str = "v1"
    max_tokens_per_record: int = 2048
    max_tool_rounds: int = 4
    repair_attempts: int = 2

    # -- service -----------------------------------------------------------
    log_level: str = "INFO"
    demo_api_key: str = "change-me"
    #: Off by default so the README's curl examples work against a fresh clone. Turned on
    #: in the deployed environment — a public endpoint with no key is somebody else's bill.
    enforce_api_key: bool = False

    @property
    def model_for_provider(self) -> str:
        """The model id that goes with ``llm_provider``."""
        return {
            "anthropic": self.anthropic_model,
            "openai": self.openai_model,
            "ollama": self.ollama_model,
            "mock": f"mock-{self.llm_provider}",
        }[self.llm_provider]


@lru_cache
def get_settings() -> Settings:
    """Process-wide settings. Cached so the .env file is parsed once."""
    return Settings()
