"""Run multimodal baseline retrieval eval (backward-compat wrapper)."""

from __future__ import annotations

import asyncio
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
    from run_multimodal_eval import main_async

    with_generation = "--with-generation" in sys.argv
    return asyncio.run(main_async(DEFAULT_CONFIG, with_generation=with_generation))


if __name__ == "__main__":
    sys.exit(main())
