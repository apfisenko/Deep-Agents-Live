"""Dataset manifest integrity tests (E-13, E-15)."""

from pathlib import Path

import pytest

from models import (
    ManifestValidationError,
    load_manifest,
    validate_manifest,
)

MANIFEST = Path(__file__).resolve().parents[1] / "datasets" / "e2e" / "e2e-qa" / "v001_2026-06-15.yaml"


def test_e2e_qa_draft_structure() -> None:
    ds = load_manifest(MANIFEST)
    assert len(ds.items) >= 20
    assert len({i.id for i in ds.items}) == len(ds.items)
    assert all(item.metadata.segment == "b2c" for item in ds.items)
    for item in ds.items:
        assert item.metadata.gt_quality in ("verified", "approximate")
        assert item.metadata.source in ("real_dialog", "synthetic")
        assert item.metadata.facts
        assert item.expected_output.answer.strip()


def test_e2e_qa_integrity_with_review() -> None:
    ds = load_manifest(MANIFEST)
    validate_manifest(ds, manifest_path=MANIFEST, require_reviewed_by=True, min_items=20)
    assert all(item.metadata.reviewed_by for item in ds.items)


def test_reviewed_by_gate_negative_on_synthetic_item() -> None:
    ds = load_manifest(MANIFEST)
    broken = ds.model_copy(deep=True)
    broken.items[0].metadata.reviewed_by = None
    with pytest.raises(ManifestValidationError, match="reviewed_by"):
        validate_manifest(broken, require_reviewed_by=True, min_items=1)


def test_version_filename_match() -> None:
    ds = load_manifest(MANIFEST)
    validate_manifest(ds, manifest_path=MANIFEST, require_reviewed_by=False, min_items=20)
