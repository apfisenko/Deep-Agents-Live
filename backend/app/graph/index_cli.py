r"""Offline graph indexing CLI (make graph-index / .\make.ps1 graph-index)."""

from __future__ import annotations

import argparse
import logging
import sys

from neo4j import Driver

from app.config import Settings, clear_settings_cache, get_settings
from app.env_loader import load_repo_env
from app.exceptions import ProviderUnavailableError
from app.graph.client import create_driver, ensure_neo4j_uri
from app.graph.cypher_file import run_cypher_file
from app.graph.entity_resolver import run_entity_resolution
from app.graph.theme_extractor import run_extraction
from app.logging_config import configure_logging
from app.paths import GRAPH_SEED_CYPHER

logger = logging.getLogger(__name__)


def _bootstrap_env() -> None:
    load_repo_env()
    clear_settings_cache()


def _open_driver() -> tuple[Driver, Settings]:
    settings = get_settings()
    if not settings.neo4j_password.strip():
        msg = "NEO4J_PASSWORD is required (set in .env)"
        raise ProviderUnavailableError(message=msg, error_code="neo4j_config")
    uri = ensure_neo4j_uri(settings.neo4j_uri)
    driver = create_driver(uri, settings.neo4j_user, settings.neo4j_password)
    driver.verify_connectivity()
    return driver, settings


def run_seed(*, database: str) -> int:
    """Apply manual seed.cypher; return number of statements executed."""
    if not GRAPH_SEED_CYPHER.is_file():
        msg = f"Seed file not found: {GRAPH_SEED_CYPHER}"
        raise FileNotFoundError(msg)

    driver, _settings = _open_driver()
    try:
        count = run_cypher_file(
            driver,
            GRAPH_SEED_CYPHER,
            database=database,
            write=True,
        )
    finally:
        driver.close()

    logger.info("Applied %s statement(s) from %s", count, GRAPH_SEED_CYPHER.name)
    return count


def run_extraction_step() -> None:
    driver, settings = _open_driver()
    try:
        run_extraction(driver, settings)
    finally:
        driver.close()


def run_resolution_step() -> None:
    driver, settings = _open_driver()
    try:
        run_entity_resolution(driver, database=settings.neo4j_database)
    finally:
        driver.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Index B2C catalog graph into Neo4j")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--seed-only",
        action="store_true",
        help="Apply data/graph/seed.cypher only (default)",
    )
    mode.add_argument(
        "--full",
        action="store_true",
        help="Seed + schema-guided theme extraction + entity resolution",
    )
    mode.add_argument(
        "--resolve-only",
        action="store_true",
        help="Run entity resolution only",
    )
    args = parser.parse_args()

    _bootstrap_env()
    settings = get_settings()
    configure_logging(settings.log_level, env=settings.env)

    try:
        if args.resolve_only:
            run_resolution_step()
            return 0

        if args.full:
            run_seed(database=settings.neo4j_database)
            run_extraction_step()
            run_resolution_step()
            return 0

        run_seed(database=settings.neo4j_database)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1
    except ProviderUnavailableError as exc:
        logger.error("%s", exc.message)
        return 1
    except Exception:
        logger.exception("Graph indexing failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
