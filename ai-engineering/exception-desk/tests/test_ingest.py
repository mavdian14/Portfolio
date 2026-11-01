"""Ingest normalisation and the idempotency key.

The hash must be computed over the *normalised* text, or the same supplier email with a
trailing newline becomes a second exception and the idempotency claim is false.
"""

from __future__ import annotations

from app.domain.inventory import normalise, source_hash


def test_whitespace_is_collapsed() -> None:
    assert normalise("a\n\nb   c\t d ") == "a b c d"


def test_sku_casing_is_canonicalised() -> None:
    assert normalise("check chr-m4k25-rgb please") == "check CHR-M4K25-RGB please"


def test_equivalent_text_hashes_the_same() -> None:
    a = "Following up on PO-88411 for chr-m4k25-rgb."
    b = "  Following   up on PO-88411 for\nCHR-M4K25-RGB.  "
    assert source_hash(a) == source_hash(b)


def test_different_text_hashes_differently() -> None:
    assert source_hash("part A is late") != source_hash("part B is late")


def test_hash_is_stable_and_hex() -> None:
    digest = source_hash("CHR-M4K25-RGB is short")
    assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)
