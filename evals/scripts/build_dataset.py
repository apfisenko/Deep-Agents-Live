"""Build dataset manifests from source data (dispatcher for evals/Makefile)."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "evals" / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "evals" / "scripts"))

from dataset_registry import ALL_DATASET_SLUGS

BUILDERS: dict[str, str] = {
    "e2e/e2e-qa": "build_e2e_qa_manifest",
    "rag/rag-format-facts": "build_rag_format_manifest",
    "rag/rag-product-facts": "build_rag_product_manifest",
    "behavior/segment-routing": "build_segment_routing_manifest",
    "behavior/funnel-to-lead": "build_funnel_to_lead_manifest",
    "edge/out-of-catalog": "build_out_of_catalog_manifest",
    "edge/objections-trust": "build_objections_trust_manifest",
}


def normalize_slug(dataset_arg: str) -> str:
    slug = dataset_arg.strip().strip("/")
    if slug == "e2e-qa":
        return "e2e/e2e-qa"
    return slug


def run_builder(slug: str) -> None:
    module_name = BUILDERS.get(slug)
    if module_name is None:
        supported = ", ".join(sorted(BUILDERS))
        msg = f"Unknown dataset {slug!r}. Supported: {supported}, all"
        raise ValueError(msg)
    module = importlib.import_module(module_name)
    module.main()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build eval dataset manifest YAML from sources")
    parser.add_argument(
        "--dataset",
        default="all",
        help=f"Dataset slug or all. Supported: {', '.join(ALL_DATASET_SLUGS)}, all",
    )
    args = parser.parse_args()

    if args.dataset == "all":
        for slug in ALL_DATASET_SLUGS:
            print(f"building: {slug}")
            run_builder(slug)
        return 0

    slug = normalize_slug(args.dataset)
    run_builder(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
