"""Logging setup for Agent Core."""

from __future__ import annotations

import logging
from pathlib import Path

_DEV_FORMAT = "%(asctime)s %(levelname)s:%(name)s:%(message)s"
_DEV_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOG_CONFIG_DEV_PATH = Path(__file__).resolve().parents[1] / "log_config.dev.json"


def configure_logging(level: str, *, env: str) -> None:
    """Configure root logger; dev uses human-readable timestamps."""
    level_num = getattr(logging, level.upper(), logging.INFO)
    if env == "dev":
        logging.basicConfig(
            level=level_num,
            format=_DEV_FORMAT,
            datefmt=_DEV_DATEFMT,
            force=True,
        )
        logging.getLogger("neo4j.notifications").setLevel(logging.WARNING)
        return
    logging.basicConfig(level=level_num, force=True)
