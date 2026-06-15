"""Integrity tests for behavior/funnel-to-lead v001."""

from pathlib import Path

import pytest

from models import ManifestValidationError, load_manifest, validate_manifest

MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "datasets"
    / "behavior"
    / "funnel-to-lead"
    / "v001_2026-06-15.yaml"
)
MIN_ITEMS = 10
VALID_FUNNEL_TOOLS = {
    "list_b2c_products",
    "create_payment_link",
    "confirm_payment",
    "save_lead",
}
VALID_STAGES = {
    "catalog",
    "payment_link",
    "payment_confirm",
    "lead_only",
    "catalog_and_payment",
}


def test_funnel_to_lead_structure() -> None:
    ds = load_manifest(MANIFEST)
    assert len(ds.items) >= MIN_ITEMS
    assert len({i.id for i in ds.items}) == len(ds.items)
    for item in ds.items:
        assert item.metadata.segment == "b2c"
        assert item.metadata.intent == "funnel"
        assert item.metadata.funnel_stage in VALID_STAGES
        assert item.metadata.facts
        assert item.expected_output.answer.strip()
        assert item.expected_output.expected_tools
        assert all(t in VALID_FUNNEL_TOOLS for t in item.expected_output.expected_tools)


def test_funnel_to_lead_stage_coverage() -> None:
    ds = load_manifest(MANIFEST)
    stages = {item.metadata.funnel_stage for item in ds.items}
    assert "payment_link" in stages
    assert "payment_confirm" in stages
    assert "catalog" in stages
    manual = sum(1 for i in ds.items if i.metadata.source == "manual")
    assert manual >= 2


def test_funnel_to_lead_integrity_with_review() -> None:
    ds = load_manifest(MANIFEST)
    validate_manifest(ds, manifest_path=MANIFEST, require_reviewed_by=True, min_items=MIN_ITEMS)
    assert all(item.metadata.reviewed_by for item in ds.items)


def test_funnel_to_lead_reviewed_by_gate() -> None:
    ds = load_manifest(MANIFEST)
    broken = ds.model_copy(deep=True)
    broken.items[0].metadata.reviewed_by = None
    with pytest.raises(ManifestValidationError, match="reviewed_by"):
        validate_manifest(broken, require_reviewed_by=True, min_items=1)
