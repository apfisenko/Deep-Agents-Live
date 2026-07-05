"""Backward-compat wrapper for build_multimodal_report.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "evals" / "configs" / "multimodal-baseline.yaml"
DEFAULT_OUT = REPO_ROOT / "evals" / "reports" / "multimodal-baseline.md"


def main() -> int:
    from build_multimodal_report import build_markdown
    from env_loader import load_repo_env
    from multimodal_config import MultimodalEvalConfig

    load_repo_env()
    cfg = MultimodalEvalConfig.from_yaml_path(DEFAULT_CONFIG)
    DEFAULT_OUT.write_text(build_markdown(cfg), encoding="utf-8")
    print(f"wrote {DEFAULT_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
