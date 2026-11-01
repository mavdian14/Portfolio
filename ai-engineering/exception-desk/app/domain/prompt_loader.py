"""Versioned prompt loading.

Prompts are files with the version in the filename, loaded by ``(name, version)``, and the
version string is recorded on every triage record and every ``llm_calls`` row.

Editing a prompt means adding a new file, never editing one in place. That is what makes it
possible to state, with data, that a prompt change helped: run the eval set against both
versions and compare.
"""

from __future__ import annotations

from functools import lru_cache

from app.config import PROMPTS_DIR


class PromptNotFound(FileNotFoundError):
    """Raised when a prompt name/version pair has no file on disk."""


@lru_cache(maxsize=64)
def load_prompt(name: str, version: str) -> str:
    """Return the text of ``{name}.{version}.md``.

    Cached, because prompts are read on every triage and never change at runtime.
    """
    path = PROMPTS_DIR / f"{name}.{version}.md"
    if not path.is_file():
        available = sorted(p.stem for p in PROMPTS_DIR.glob("*.md"))
        raise PromptNotFound(
            f"prompt {name!r} version {version!r} not found at {path}. "
            f"Available: {', '.join(available) or 'none'}"
        )
    return path.read_text(encoding="utf-8").strip()


def available_prompts() -> list[str]:
    """Every prompt on disk, as ``name.version``. Used by /readyz and the tests."""
    return sorted(p.stem for p in PROMPTS_DIR.glob("*.md"))


def render(name: str, version: str, **values: object) -> str:
    """Load a prompt and substitute ``{placeholders}``.

    Deliberately ``str.format`` and not a template engine: a prompt that needs logic
    belongs in code, not in a text file.
    """
    template = load_prompt(name, version)
    try:
        return template.format(**values)
    except KeyError as exc:
        raise KeyError(
            f"prompt {name}.{version} expects a value for {exc}; got {sorted(values)}"
        ) from exc
