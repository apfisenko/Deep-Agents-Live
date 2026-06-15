"""Load and resolve eval run configs from evals/configs/*.yaml (E-6)."""

from __future__ import annotations

import logging
from pathlib import Path

from app.agent.run_config import RunConfig
from app.env_loader import load_repo_env
from app.exceptions import ConfigNotFoundError
from app.paths import EVALS_CONFIGS_DIR

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_ID = "baseline-react-inmemory"


def _config_path(config_id: str) -> Path:
    safe_id = config_id.removesuffix(".yaml")
    return EVALS_CONFIGS_DIR / f"{safe_id}.yaml"


def _load_all_configs() -> dict[str, RunConfig]:
    if not EVALS_CONFIGS_DIR.is_dir():
        msg = f"Eval configs directory not found: {EVALS_CONFIGS_DIR}"
        raise ConfigNotFoundError(msg, config_id=DEFAULT_CONFIG_ID)

    load_repo_env()

    configs: dict[str, RunConfig] = {}
    for path in sorted(EVALS_CONFIGS_DIR.glob("*.yaml")):
        cfg = RunConfig.from_yaml_path(path)
        if cfg.config_id != path.stem:
            msg = f"config_id mismatch in {path.name}: {cfg.config_id!r} != {path.stem!r}"
            raise ValueError(msg)
        configs[cfg.config_id] = cfg
        logger.debug("Loaded run config", extra={"config_id": cfg.config_id})

    if DEFAULT_CONFIG_ID not in configs:
        msg = f"Default config {DEFAULT_CONFIG_ID!r} is missing in {EVALS_CONFIGS_DIR}"
        raise ConfigNotFoundError(msg, config_id=DEFAULT_CONFIG_ID)

    return configs


def get_default_config_id() -> str:
    return DEFAULT_CONFIG_ID


def get_run_config(config_id: str | None = None) -> RunConfig:
    cid = config_id or DEFAULT_CONFIG_ID
    configs = _load_all_configs()
    if cid not in configs:
        msg = f"Unknown config_id: {cid}"
        raise ConfigNotFoundError(msg, config_id=cid)
    return configs[cid]


def list_config_ids() -> list[str]:
    return sorted(_load_all_configs())


def reset_config_registry() -> None:
    """No-op: configs are loaded fresh on each resolve (eval hot-reload)."""
