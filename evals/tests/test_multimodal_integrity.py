"""Integrity tests for multimodal segment datasets."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MM_DIR = REPO_ROOT / "evals" / "datasets" / "multimodal"

SEGMENTS = {
    "s1-text": ("S1_text", 9),
    "s2-chart": ("S2_chart", 11),
    "s3-layout": ("S3_layout", 10),
    "s4-multi": ("S4_multi", 6),
    "s5-unanswerable": ("S5_unanswerable", 6),
}


def _latest_manifest(subdir: str) -> Path:
    base = MM_DIR / subdir
    candidates = sorted(base.glob("v001_*.yaml"))
    assert candidates, f"missing manifest under {base}"
    return candidates[-1]


def test_multimodal_manifests_exist() -> None:
    for subdir, (_, min_items) in SEGMENTS.items():
        path = _latest_manifest(subdir)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["group"] == "multimodal"
        assert len(data["items"]) >= min_items


def test_multimodal_gold_pages_in_range() -> None:
    for subdir in SEGMENTS:
        path = _latest_manifest(subdir)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for item in data["items"]:
            for page in item["metadata"].get("gold_pages") or []:
                assert 1 <= page <= 66, f"{item['id']}: page {page} out of range"


def test_s5_has_empty_gold_pages() -> None:
    path = _latest_manifest("s5-unanswerable")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for item in data["items"]:
        assert item["metadata"]["multimodal_segment"] == "S5_unanswerable"
        assert item["metadata"]["gold_pages"] == []


def test_s4_multi_has_multiple_gold_pages() -> None:
    path = _latest_manifest("s4-multi")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    multi = [item for item in data["items"] if len(item["metadata"]["gold_pages"]) > 1]
    assert len(multi) >= 3
