"""dataset_registry tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from app.agent.run_config import RunConfig
from dataset_registry import (
    ALL_DATASET_SLUGS,
    resolve_all_dataset_targets,
    resolve_dataset_target,
    slug_to_run_suffix,
)

EVALS_ROOT = Path(__file__).resolve().parents[1]
CONFIG = EVALS_ROOT / "configs" / "baseline-react-inmemory.yaml"


def test_all_dataset_slugs_count() -> None:
    assert len(ALL_DATASET_SLUGS) == 8


def test_resolve_rag_format_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_DATASET_PREFIX", raising=False)
    monkeypatch.delenv("EVAL_DATASET_NAME", raising=False)
    config = RunConfig.from_yaml_path(CONFIG)
    target = resolve_dataset_target(config, "rag/rag-format-facts")
    assert target.full_name == "rag/rag-format-facts/v001"
    assert target.manifest_path.name.startswith("v001_")


def test_resolve_all_targets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_DATASET_PREFIX", raising=False)
    monkeypatch.delenv("EVAL_DATASET_NAME", raising=False)
    config = RunConfig.from_yaml_path(CONFIG)
    targets = resolve_all_dataset_targets(config)
    assert len(targets) == 8


def test_resolve_unknown_dataset() -> None:
    config = RunConfig.from_yaml_path(CONFIG)
    with pytest.raises(ValueError, match="Unsupported"):
        resolve_dataset_target(config, "unknown/dataset")


def test_slug_to_run_suffix() -> None:
    assert slug_to_run_suffix("rag/rag-format-facts") == "rag-rag-format-facts"
