"""Integrity tests for graphrag segment datasets."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPHAG_DIR = REPO_ROOT / "evals" / "datasets" / "graphrag"


def _latest_manifest(subdir: str) -> Path:
    base = GRAPHAG_DIR / subdir
    candidates = sorted(base.glob("v001_*.yaml"))
    assert candidates, f"missing manifest under {base}"
    return candidates[-1]


def test_graphrag_multi_hop_manifest() -> None:
    path = _latest_manifest("multi-hop")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["group"] == "graphrag"
    assert len(data["items"]) >= 10
    for item in data["items"]:
        assert item["metadata"]["question_segment"] == "multi-hop"
        assert item["metadata"]["required_entities"]


def test_graphrag_global_manifest() -> None:
    path = _latest_manifest("global")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert len(data["items"]) == 6
    for item in data["items"]:
        assert item["metadata"]["question_segment"] == "global"


def test_graphrag_single_hop_manifest() -> None:
    path = _latest_manifest("single-hop")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert len(data["items"]) == 3
    for item in data["items"]:
        assert item["metadata"]["question_segment"] == "single-hop"
