"""End-to-end HTTP behaviour against a real Postgres and the mock provider."""

from __future__ import annotations

from httpx import AsyncClient

NOTE = (
    "Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB) — our production line is "
    "fully committed through December, so we cannot confirm the Nov 14 date."
)


async def test_healthz_is_unauthenticated(client: AsyncClient) -> None:
    r = await client.get("/healthz")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


async def test_readyz_reports_each_dependency(client: AsyncClient) -> None:
    r = await client.get("/readyz")
    assert r.status_code == 200
    body = r.json()
    assert body["ready"] is True
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["provider"] == "mock"


async def test_triage_returns_a_grounded_record(client: AsyncClient) -> None:
    r = await client.post("/triage", json={"text": NOTE})
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["sku"] == "CHR-M4K25-RGB"
    assert body["severity"] in ("critical", "high", "medium", "low")
    assert body["status"] == "needs_review"
    assert body["duplicate"] is False

    # The record must carry the evidence it was built from.
    assert body["evidence"], "a triaged record with no evidence is not auditable"
    tools_used = {e["tool"] for e in body["evidence"]}
    assert "get_sku_status" in tools_used
    evidence_keys = {"round", "tool", "arguments", "result", "is_error"}
    assert all(evidence_keys <= set(e) for e in body["evidence"])

    # ...and its provenance.
    p = body["provenance"]
    assert p["provider"] == "mock"
    assert p["prompt_version"] == "v1"
    assert p["llm_calls"] >= 2  # the tool loop plus the extraction
    assert p["input_tokens"] > 0


async def test_the_record_is_persisted_and_readable(client: AsyncClient) -> None:
    created = (await client.post("/triage", json={"text": NOTE})).json()

    fetched = await client.get(f"/exceptions/{created['id']}")
    assert fetched.status_code == 200
    got = fetched.json()
    assert got["id"] == created["id"]
    assert got["sku"] == created["sku"]
    assert len(got["evidence"]) == len(created["evidence"])


async def test_identical_text_is_not_triaged_twice(client: AsyncClient) -> None:
    first = (await client.post("/triage", json={"text": NOTE})).json()
    second = (await client.post("/triage", json={"text": NOTE})).json()

    assert second["duplicate"] is True
    assert second["id"] == first["id"]

    queue = (await client.get("/exceptions")).json()
    assert queue["count"] == 1, "the same message must not create a second exception"


async def test_whitespace_variants_are_the_same_exception(client: AsyncClient) -> None:
    await client.post("/triage", json={"text": NOTE})
    variant = f"  {NOTE.replace(' ', '  ')}  "
    second = (await client.post("/triage", json={"text": variant})).json()
    assert second["duplicate"] is True


async def test_queue_filters_by_severity(client: AsyncClient) -> None:
    created = (await client.post("/triage", json={"text": NOTE})).json()
    matching = (await client.get("/exceptions", params={"severity": created["severity"]})).json()
    assert matching["count"] == 1
    empty = (await client.get("/exceptions", params={"severity": "no-such-severity"})).json()
    assert empty["count"] == 0


async def test_source_kind_is_inferred_when_not_given(client: AsyncClient) -> None:
    body = (await client.post("/triage", json={"text": NOTE})).json()
    assert body["source_kind"] == "supplier_email"


async def test_unknown_exception_returns_404(client: AsyncClient) -> None:
    r = await client.get("/exceptions/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


async def test_empty_text_is_rejected(client: AsyncClient) -> None:
    r = await client.post("/triage", json={"text": ""})
    assert r.status_code == 422


async def test_cost_endpoint_totals_the_calls(client: AsyncClient) -> None:
    await client.post("/triage", json={"text": NOTE})
    r = await client.get("/metrics/cost", params={"days": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["total_calls"] >= 2
    assert body["rows"] and body["rows"][0]["provider"] == "mock"


async def test_index_serves_the_ui(client: AsyncClient) -> None:
    r = await client.get("/")
    assert r.status_code == 200
    assert "exception-desk" in r.text
