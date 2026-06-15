"""Integrity tests for behavior/segment-routing v001."""

from pathlib import Path

import pytest

from models import ManifestValidationError, load_manifest, validate_manifest

MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "datasets"
    / "behavior"
    / "segment-routing"
    / "v001_2026-06-15.yaml"
)
MIN_ITEMS = 10


def test_segment_routing_structure() -> None:
    ds = load_manifest(MANIFEST)
    assert len(ds.items) >= MIN_ITEMS
    assert len({i.id for i in ds.items}) == len(ds.items)
    for item in ds.items:
        assert item.metadata.intent == "segment-route"
        assert item.metadata.segment in ("b2b", "b2c")
        assert item.metadata.facts
        assert item.expected_output.answer.strip()


def test_segment_routing_b2b_must_not() -> None:
    ds = load_manifest(MANIFEST)
    b2b = [i for i in ds.items if i.metadata.segment == "b2b"]
    b2c = [i for i in ds.items if i.metadata.segment == "b2c"]
    assert len(b2b) >= 4
    assert len(b2c) >= 4
    for item in b2b:
        assert "create_payment_link" in item.metadata.must_not


def test_segment_routing_integrity_with_review() -> None:
    ds = load_manifest(MANIFEST)
    validate_manifest(ds, manifest_path=MANIFEST, require_reviewed_by=True, min_items=MIN_ITEMS)
    assert all(item.metadata.reviewed_by for item in ds.items)


def test_segment_routing_reviewed_by_gate() -> None:
    ds = load_manifest(MANIFEST)
    broken = ds.model_copy(deep=True)
    broken.items[0].metadata.reviewed_by = None
    with pytest.raises(ManifestValidationError, match="reviewed_by"):
        validate_manifest(broken, require_reviewed_by=True, min_items=1)
