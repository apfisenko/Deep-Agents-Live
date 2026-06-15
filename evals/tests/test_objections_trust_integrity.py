"""Integrity tests for edge/objections-trust v001."""

from pathlib import Path

import pytest

from models import ManifestValidationError, load_manifest, validate_manifest

MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "datasets"
    / "edge"
    / "objections-trust"
    / "v001_2026-06-15.yaml"
)
MIN_ITEMS = 10
VALID_INTENTS = {"objection", "format-mismatch"}


def test_objections_trust_structure() -> None:
    ds = load_manifest(MANIFEST)
    assert len(ds.items) >= MIN_ITEMS
    assert len({i.id for i in ds.items}) == len(ds.items)
    for item in ds.items:
        assert item.metadata.segment == "b2c"
        assert item.metadata.intent in VALID_INTENTS
        assert item.metadata.facts
        assert item.expected_output.answer.strip()


def test_objections_trust_intent_mix() -> None:
    ds = load_manifest(MANIFEST)
    intents = {item.metadata.intent for item in ds.items}
    assert intents == VALID_INTENTS
    assert sum(1 for i in ds.items if i.metadata.intent == "objection") >= 6


def test_objections_trust_integrity_with_review() -> None:
    ds = load_manifest(MANIFEST)
    validate_manifest(ds, manifest_path=MANIFEST, require_reviewed_by=True, min_items=MIN_ITEMS)
    assert all(item.metadata.reviewed_by for item in ds.items)


def test_objections_trust_reviewed_by_gate() -> None:
    ds = load_manifest(MANIFEST)
    broken = ds.model_copy(deep=True)
    broken.items[0].metadata.reviewed_by = None
    with pytest.raises(ManifestValidationError, match="reviewed_by"):
        validate_manifest(broken, require_reviewed_by=True, min_items=1)
