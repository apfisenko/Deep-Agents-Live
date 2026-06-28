"""Dataset slug registry for multi-dataset eval runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from models import (
    DATASETS_DIR,
    RunConfig,
    langfuse_dataset_name,
    load_manifest,
    validate_manifest,
)

DATASET_MIN_ITEMS: dict[str, int] = {
    "e2e/e2e-qa": 20,
    "rag/rag-format-facts": 15,
    "rag/rag-product-facts": 15,
    "behavior/segment-routing": 10,
    "behavior/funnel-to-lead": 10,
    "edge/out-of-catalog": 8,
    "edge/objections-trust": 10,
    "edge/error-analysis-hits": 5,
    "graphrag/multi-hop": 10,
    "graphrag/global": 6,
    "graphrag/single-hop": 3,
}

ALL_DATASET_SLUGS = tuple(DATASET_MIN_ITEMS.keys())

GRAPHAG_DATASET_SLUGS = (
    "graphrag/multi-hop",
    "graphrag/global",
    "graphrag/single-hop",
)

CONFIG_DATASET_SLUGS: dict[str, tuple[str, ...]] = {
    "graphrag-baseline": GRAPHAG_DATASET_SLUGS,
}


def dataset_slugs_for_config(config: RunConfig) -> tuple[str, ...]:
    override = CONFIG_DATASET_SLUGS.get(config.config_id)
    if override is not None:
        return override
    return ALL_DATASET_SLUGS


@dataclass(frozen=True)
class DatasetTarget:
    slug: str
    full_name: str
    version: str
    manifest_path: Path
    group: str
    dataset: str


def config_key_for_slug(slug: str) -> str:
    return slug.rsplit("/", maxsplit=1)[-1]


def manifest_path_for_slug(slug: str, version: str) -> Path:
    base = DATASETS_DIR.joinpath(*slug.split("/"))
    candidates = sorted(base.glob(f"{version}_*.yaml"))
    if not candidates:
        msg = f"No manifest for {slug} version {version} under {base}"
        raise FileNotFoundError(msg)
    return candidates[0]


def should_apply_langfuse_name_override(slug: str, *, apply_name_override: bool) -> bool:
    """GraphRAG segment datasets always use manifest path names in Langfuse."""
    if slug.startswith("graphrag/"):
        return False
    return apply_name_override


def resolve_dataset_target(
    config: RunConfig,
    dataset_arg: str,
    *,
    apply_name_override: bool = False,
) -> DatasetTarget:
    slug = dataset_arg.strip().strip("/")
    if slug == "e2e-qa":
        slug = "e2e/e2e-qa"
    if slug not in DATASET_MIN_ITEMS:
        supported = ", ".join(ALL_DATASET_SLUGS)
        msg = f"Unsupported dataset: {dataset_arg}. Supported: {supported}, all"
        raise ValueError(msg)

    key = config_key_for_slug(slug)
    version = config.datasets.get(key, "v001")
    manifest_path = manifest_path_for_slug(slug, version)
    manifest = load_manifest(manifest_path)
    min_items = DATASET_MIN_ITEMS[slug]
    validate_manifest(
        manifest,
        manifest_path=manifest_path,
        require_reviewed_by=True,
        min_items=min_items,
    )
    full_name = langfuse_dataset_name(
        manifest,
        apply_name_override=should_apply_langfuse_name_override(
            slug,
            apply_name_override=apply_name_override,
        ),
    )
    return DatasetTarget(
        slug=slug,
        full_name=full_name,
        version=version,
        manifest_path=manifest_path,
        group=manifest.group,
        dataset=manifest.dataset,
    )


def resolve_all_dataset_targets(config: RunConfig) -> list[DatasetTarget]:
    return [resolve_dataset_target(config, slug) for slug in dataset_slugs_for_config(config)]


def slug_to_run_suffix(slug: str) -> str:
    return slug.replace("/", "-")
