"""Langfuse dataset naming tests."""


import pytest

from models import DatasetManifest, langfuse_dataset_name


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
    manifest = _sample_manifest()
    assert langfuse_dataset_name(manifest) == "e2e/e2e-qa/v001"


def test_langfuse_dataset_name_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EVAL_DATASET_PREFIX", "dev")
    manifest = _sample_manifest()
    assert langfuse_dataset_name(manifest) == "dev/e2e/e2e-qa/v001"
