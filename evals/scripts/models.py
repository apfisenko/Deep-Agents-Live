"""Pydantic models for eval datasets and run configs (E-12, E-15)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.agent.run_config import RunConfig

DATASETS_DIR = REPO_ROOT / "evals" / "datasets"

Segment = Literal["b2c", "b2b"]
GtQuality = Literal["verified", "approximate"]
Source = Literal["real_dialog", "synthetic", "manual"]


class DatasetItemInput(BaseModel):
    message: str = Field(min_length=1)
    channel: Literal["web", "telegram"] = "web"


class ExpectedOutput(BaseModel):
    answer: str = Field(min_length=1)
    expected_tools: list[str] = Field(default_factory=list)


class DatasetItemMetadata(BaseModel):
    segment: Segment
    intent: str
    source: Source
    gt_quality: GtQuality
    reviewed_by: str | None = None
    product_id: str | None = None
    nearest_product_id: str | None = None
    facts: list[str] = Field(default_factory=list)
    source_chat: str | None = None
    legacy_id: str | None = None
    must_not: list[str] = Field(default_factory=list)
    funnel_stage: str | None = None
    source_trace_id: str | None = None
    error_category: str | None = None
    source_run: str | None = None
    source_item_id: str | None = None
    target_dataset: str | None = None

    @field_validator("facts")
    @classmethod
    def facts_non_empty(cls, value: list[str]) -> list[str]:
        if not value:
            msg = "facts[] must not be empty"
            raise ValueError(msg)
        return value


class DatasetItem(BaseModel):
    id: str = Field(min_length=1)
    input: DatasetItemInput
    expected_output: ExpectedOutput
    metadata: DatasetItemMetadata


class DatasetManifest(BaseModel):
    dataset: str
    group: Literal["e2e", "rag", "behavior", "edge"]
    version: str
    created: str
    description: str
    items: list[DatasetItem]

    @field_validator("items")
    @classmethod
    def unique_ids(cls, value: list[DatasetItem]) -> list[DatasetItem]:
        ids = [item.id for item in value]
        if len(ids) != len(set(ids)):
            msg = "duplicate item ids in manifest"
            raise ValueError(msg)
        return value


class ManifestValidationError(ValueError):
    """Raised when manifest fails eval validation rules."""


def load_manifest(path: str | Path) -> DatasetManifest:
    manifest_path = Path(path)
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Invalid YAML root: {manifest_path}"
        raise TypeError(msg)
    return DatasetManifest.model_validate(raw)


def discover_manifests(group_name: str | None = None) -> list[Path]:
    if not DATASETS_DIR.exists():
        return []
    paths = sorted(DATASETS_DIR.rglob("v*.yaml"))
    if group_name and group_name != "all":
        needle = group_name.replace("\\", "/")
        paths = [p for p in paths if needle in str(p.relative_to(DATASETS_DIR)).replace("\\", "/")]
    return paths


def validate_manifest(
    manifest: DatasetManifest,
    *,
    manifest_path: Path | None = None,
    require_reviewed_by: bool = True,
    min_items: int = 1,
) -> None:
    if len(manifest.items) < min_items:
        msg = f"manifest has {len(manifest.items)} items, need >= {min_items}"
        raise ManifestValidationError(msg)

    if manifest_path is not None:
        if manifest.version not in manifest_path.name:
            msg = f"version {manifest.version!r} not in filename {manifest_path.name}"
            raise ManifestValidationError(msg)

    for item in manifest.items:
        if require_reviewed_by and not item.metadata.reviewed_by:
            msg = f"{item.id}: missing reviewed_by (E-13)"
            raise ManifestValidationError(msg)
        if isinstance(item.expected_output, (int, bytes)):
            msg = f"{item.id}: expected_output not human-readable (E-12)"
            raise ManifestValidationError(msg)


def manifest_to_langfuse_item(manifest: DatasetManifest, item: DatasetItem) -> dict[str, Any]:
    metadata = item.metadata.model_dump(exclude_none=True)
    facts = metadata.pop("facts", [])
    metadata["facts_count"] = len(facts)
    if facts:
        preview = "; ".join(facts[:3])
        metadata["facts_preview"] = preview[:200]
    return {
        "id": item.id,
        "input": item.input.model_dump(),
        "expectedOutput": item.expected_output.model_dump(),
        "metadata": metadata,
    }


def langfuse_dataset_name(manifest: DatasetManifest) -> str:
    base = f"{manifest.group}/{manifest.dataset}/{manifest.version}"
    prefix = os.environ.get("EVAL_DATASET_PREFIX", "").strip().strip("/")
    if prefix:
        return f"{prefix}/{base}"
    return base


__all__ = [
    "DatasetItem",
    "DatasetManifest",
    "ManifestValidationError",
    "RunConfig",
    "discover_manifests",
    "langfuse_dataset_name",
    "load_manifest",
    "manifest_to_langfuse_item",
    "validate_manifest",
]
