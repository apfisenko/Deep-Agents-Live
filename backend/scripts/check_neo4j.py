"""Smoke check for Neo4j connectivity (sprint-06, task 04)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import clear_settings_cache, get_settings
from app.env_loader import load_repo_env
from app.exceptions import ProviderUnavailableError
from app.graph.client import ensure_neo4j_uri, verify_connectivity


def _fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def _bootstrap_env() -> None:
    load_repo_env()
    clear_settings_cache()


def run_status(*, quiet: bool = False) -> None:
    _bootstrap_env()
    settings = get_settings()
    if not settings.neo4j_password.strip():
        _fail("NEO4J_PASSWORD is required (set in .env)")

    uri = ensure_neo4j_uri(settings.neo4j_uri)
    os.environ["NEO4J_URI"] = uri

    try:
        verify_connectivity(uri, settings.neo4j_user, settings.neo4j_password)
    except ProviderUnavailableError as exc:
        _fail(str(exc))
    except Exception as exc:  # noqa: BLE001 — surface driver errors in smoke CLI
        _fail(f"Neo4j connectivity check failed: {exc}")

    if not quiet:
        print("Connection OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Neo4j connectivity smoke check")
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status"],
        help="check command (default: status)",
    )
    parser.add_argument("--quiet", action="store_true", help="exit 0 without printing OK")
    args = parser.parse_args()

    if args.command == "status":
        run_status(quiet=args.quiet)


if __name__ == "__main__":
    main()
