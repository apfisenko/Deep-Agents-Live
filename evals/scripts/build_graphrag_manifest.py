"""Build graphrag dataset YAML manifests from JSON sources (sprint-06 task 02)."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from models import DatasetManifest, validate_manifest

GRAPHAG_DIR = REPO_ROOT / "evals" / "datasets" / "graphrag"
CREATED = date.today().isoformat()
REVIEWED_BY = "sprint-06-task-02"

SOURCE_FILES: dict[str, tuple[str, str, int]] = {
    "graphrag/multi-hop": ("multi_hop.json", "GraphRAG multi-hop questions (flat RAG stress)", 10),
    "graphrag/global": ("global.json", "GraphRAG global/aggregate questions (flat RAG stress)", 6),
    "graphrag/single-hop": ("single_hop.json", "GraphRAG single-hop guard items", 3),
}


def load_json_items(path: Path) -> list[dict[str, object]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        msg = f"Expected JSON array in {path}"
        raise TypeError(msg)
    return raw


def item_to_manifest_row(row: dict[str, object]) -> dict[str, object]:
    question_segment = str(row["segment"])
    required_entities = [str(e) for e in row["required_entities"]]  # type: ignore[index]
    return {
        "id": str(row["id"]),
        "input": {
            "message": str(row["question"]),
            "channel": "web",
        },
        "expected_output": {
            "answer": str(row["reference_answer"]),
        },
        "metadata": {
            "segment": "b2c",
            "question_segment": question_segment,
            "intent": question_segment,
            "source": "synthetic",
            "gt_quality": "verified",
            "reviewed_by": REVIEWED_BY,
            "required_entities": required_entities,
            "facts": required_entities,
        },
    }


def build_manifest(slug: str) -> Path:
    filename, description, min_items = SOURCE_FILES[slug]
    source_path = GRAPHAG_DIR / filename
    dataset_name = slug.rsplit("/", maxsplit=1)[-1]
    items = [item_to_manifest_row(row) for row in load_json_items(source_path)]

    manifest_dict = {
        "dataset": dataset_name,
        "group": "graphrag",
        "version": "v001",
        "created": CREATED,
        "description": description,
        "items": items,
    }
    manifest = DatasetManifest.model_validate(manifest_dict)
    validate_manifest(
        manifest,
        require_reviewed_by=True,
        min_items=min_items,
    )

    out_dir = GRAPHAG_DIR / dataset_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"v001_{CREATED}.yaml"
    out_path.write_text(
        yaml.safe_dump(manifest_dict, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"wrote {out_path} ({len(items)} items)")
    return out_path


def main() -> int:
    for slug in SOURCE_FILES:
        build_manifest(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
