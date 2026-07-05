"""Index multimodal naive-text corpus into Qdrant (backward-compat wrapper)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
EVALS_ROOT = REPO_ROOT / "evals"
DEFAULT_CONFIG = EVALS_ROOT / "configs" / "multimodal-baseline.yaml"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def main() -> int:
    from index_multimodal import index_from_config

    force = "--force" in sys.argv
    return index_from_config(DEFAULT_CONFIG, force=force)


if __name__ == "__main__":
    sys.exit(main())
