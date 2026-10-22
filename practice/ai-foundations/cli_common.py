"""
Shared plumbing for the three AI Foundations scripts: argument parsing, provider resolution,
console formatting, and the pydantic -> strict-JSON-schema transform.

Kept separate so each numbered script reads as the lesson and nothing else.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import textwrap
import time
from typing import Any, Iterable, Sequence, cast

from llm_client import (
    DEFAULT_MODELS,
    BaseClient,
    Provider,
    credential_status,
    load_env,
    make_client,
)

PROVIDERS: tuple[str, ...] = ("anthropic", "openai")
RULE = "-" * 78


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", choices=("both", "anthropic", "openai"), default="both",
                        help="which provider(s) to exercise (default: both)")
    parser.add_argument("--model", default=None,
                        help="override the model id for every provider (default: from .env)")
    parser.add_argument("--live", action="store_true",
                        help="call the real APIs; without this the script runs offline against a "
                             "deterministic mock provider")
    parser.add_argument("--json", action="store_true", help="also dump collected results as JSON")
    return parser


def resolve_clients(args: argparse.Namespace) -> tuple[dict[str, BaseClient], bool, dict[str, bool]]:
    """Return ({provider: client}, dry_run, credential_status). Live mode skips keyless providers."""
    load_env()
    status = credential_status()
    dry_run = not args.live
    wanted = list(PROVIDERS) if args.provider == "both" else [args.provider]

    if dry_run:
        print("mode: DRY RUN — offline mock provider. Request payloads are the real ones;")
        print("      responses are deterministic stand-ins. Use --live (with keys) for real calls.")
    else:
        missing = [p for p in wanted if not status[p]]
        if missing:
            print(f"note: no API key found for {', '.join(missing)} — skipping those providers")
            wanted = [p for p in wanted if status[p]]
        if not wanted:
            print("error: --live needs ANTHROPIC_API_KEY and/or OPENAI_API_KEY (env or .env)")
            sys.exit(2)

    clients: dict[str, BaseClient] = {}
    for provider in wanted:
        clients[provider] = make_client(cast(Provider, provider),
                                        model=args.model or DEFAULT_MODELS[provider],
                                        dry_run=dry_run)
    return clients, dry_run, status


def header(title: str, clients: dict[str, BaseClient], dry_run: bool) -> None:
    print(RULE)
    print(textwrap.fill(title, width=78))
    print(RULE)
    for provider, client in clients.items():
        print(f"  {provider:<10} model={client.model:<26} transport={'mock' if dry_run else 'live'}")
    print()


def section(number: str, title: str) -> None:
    line = f"{number}. {title}"
    print(f"\n{line}\n{'-' * min(len(line), 78)}")


def note(text: str) -> None:
    print(f"  note: {textwrap.fill(text, width=72, subsequent_indent=' ' * 8)}")


def table(headers: Sequence[str], rows: Iterable[Sequence[Any]], indent: int = 2) -> None:
    rows = [[("" if cell is None else str(cell)) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row[:len(widths)]):
            widths[i] = max(widths[i], len(cell))
    pad = " " * indent
    print(pad + "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)).rstrip())
    print(pad + "  ".join("-" * w for w in widths))
    for row in rows:
        print(pad + "  ".join(row[i].ljust(widths[i]) for i in range(len(headers))).rstrip())


def kv(pairs: Iterable[tuple[str, Any]], indent: int = 2) -> None:
    pairs = [(str(k), str(v)) for k, v in pairs]
    if not pairs:
        return
    width = max(len(k) for k, _ in pairs)
    pad = " " * indent
    for key, value in pairs:
        print(f"{pad}{key.ljust(width)} : {value}")


def json_block(obj: Any, indent: int = 4, max_lines: int | None = None) -> None:
    lines = json.dumps(obj, indent=2, default=str).splitlines()
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines] + [f"  ... ({len(lines) - max_lines} more lines)"]
    print(textwrap.indent("\n".join(lines), " " * indent))


def emit_json(args: argparse.Namespace, payload: Any) -> None:
    if getattr(args, "json", False):
        print(f"\n{RULE}\nJSON summary\n{RULE}")
        print(json.dumps(payload, indent=2, default=str))


# --------------------------------------------------------------------------------------
# pydantic -> JSON schema helpers (the strict-mode transform the SDKs do internally)
# --------------------------------------------------------------------------------------


def to_strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Apply the strict-mode rules recursively, the way the OpenAI SDK does for strict=True:

      * every object gets additionalProperties: false
      * every property is listed in `required`
      * an optional property becomes a *nullable* type instead of being absent from `required`
      * `default` keys are dropped (a required field with a default is contradictory)

    Anthropic applies a similar transform on the server for its structured outputs; doing it by
    hand once makes both paths readable instead of magic.
    """
    out = copy.deepcopy(schema)

    def is_nullable(spec: dict[str, Any]) -> bool:
        if spec.get("type") == "null":
            return True
        return any(branch.get("type") == "null" for branch in spec.get("anyOf", []))

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" or "properties" in node:
                props = node.get("properties") or {}
                originally_required = set(node.get("required", []))
                for name, spec in list(props.items()):
                    if not isinstance(spec, dict):
                        continue
                    spec.pop("default", None)
                    if name not in originally_required and not is_nullable(spec):
                        props[name] = {"anyOf": [spec, {"type": "null"}]}
                node["additionalProperties"] = False
                node["required"] = list(props)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


def schema_field_rows(schema: dict[str, Any]) -> list[list[str]]:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    rows: list[list[str]] = []
    for name, spec in props.items():
        if "type" in spec:
            kind = spec["type"]
        elif "$ref" in spec:
            kind = "object"
        elif "anyOf" in spec:
            kind = "union"
        else:
            kind = "?"
        if "enum" in spec:
            extra = "enum: " + ",".join(str(v) for v in spec["enum"])
        elif "$ref" in spec:
            extra = spec["$ref"].split("/")[-1]
        elif "anyOf" in spec:
            extra = " | ".join(
                b.get("type") or b.get("$ref", "?").split("/")[-1] for b in spec["anyOf"]
            )
        else:
            extra = ""
        rows.append([name, kind, "yes" if name in required else "no", extra])
    return rows


class Timer:
    """Wall-clock timer usable as a context manager."""

    def __enter__(self) -> "Timer":
        self.started = time.perf_counter()
        self.elapsed = 0.0
        return self

    def __exit__(self, *exc: Any) -> bool:
        self.elapsed = time.perf_counter() - self.started
        return False
