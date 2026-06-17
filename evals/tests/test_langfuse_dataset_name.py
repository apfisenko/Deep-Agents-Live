"""Langfuse dataset naming tests."""

import pytest

from models import DatasetManifest, langfuse_dataset_base_name, langfuse_dataset_name


def _sample_manifest() -> DatasetManifest:
    return DatasetManifest.model_validate(
        {
            "dataset": "e2e-qa",
            "group": "e2e",
            "version": "v001",
            "created": "2026-06-15",
            "description": "test",
            "items": [
                {
                    "id": "e2e-qa-syn-001",
                    "input": {"message": "test", "channel": "web"},
                    "expected_output": {"answer": "ok"},
                    "metadata": {
                        "segment": "b2c",
                        "intent": "product_fit",
                        "source": "synthetic",
                        "gt_quality": "verified",
                        "reviewed_by": "test",
                        "facts": ["fact"],
                    },
                },
            ],
        },
    )


def test_langfuse_dataset_name_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_DATASET_PREFIX", raising=False)
    monkeypatch.delenv("EVAL_DATASET_NAME", raising=False)
    manifest = _sample_manifest()
    assert langfuse_dataset_name(manifest) == "e2e/e2e-qa/v001"


def test_langfuse_dataset_name_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_DATASET_NAME", raising=False)
    monkeypatch.setenv("EVAL_DATASET_PREFIX", "dev")
    manifest = _sample_manifest()
    assert langfuse_dataset_name(manifest) == "dev/e2e/e2e-qa/v001"


def test_langfuse_dataset_name_with_explicit_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_DATASET_PREFIX", raising=False)
    monkeypatch.setenv("EVAL_DATASET_NAME", "custom/e2e-qa/v001")
    manifest = _sample_manifest()
    assert langfuse_dataset_name(manifest) == "e2e/e2e-qa/v001"
    assert langfuse_dataset_name(manifest, apply_name_override=True) == "custom/e2e-qa/v001"


def test_langfuse_dataset_name_explicit_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EVAL_DATASET_NAME", "e2e/e2e-qa/v001")
    monkeypatch.setenv("EVAL_DATASET_PREFIX", "deep_agents_live_v001")
    manifest = _sample_manifest()
    assert langfuse_dataset_name(manifest, apply_name_override=True) == (
        "deep_agents_live_v001/e2e/e2e-qa/v001"
    )


def test_langfuse_dataset_base_name_ignores_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EVAL_DATASET_NAME", "my-dataset")
    monkeypatch.setenv("EVAL_DATASET_PREFIX", "prod")
    manifest = _sample_manifest()
    assert langfuse_dataset_base_name(manifest, apply_name_override=True) == "my-dataset"
