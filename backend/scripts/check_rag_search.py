"""Smoke checks for RAG search against live Qdrant (sprint-05, task 04)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import clear_settings_cache, get_settings
from app.env_loader import load_repo_env
from app.integrations.qdrant_url import ensure_qdrant_url
from app.tools.registry import search_knowledge_base_tool
from qdrant_client import QdrantClient

DEFAULT_B2C_QUERY = "Deep Agents курс для разработчиков"
DEFAULT_FILTER_QUERY = "обучение RAG и AI-агенты"


def _ok(message: str) -> None:
    print(f"OK: {message}")


def _fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def _bootstrap_env() -> None:
    """Load repo .env into os.environ (same as backend / make index)."""
    load_repo_env()
    clear_settings_cache()


def _require_openrouter_key() -> None:
    if not get_settings().openrouter_api_key.strip():
        _fail("OPENROUTER_API_KEY is required for embedding query (set in .env)")


def _require_qdrant_backend() -> None:
    backend = get_settings().vector_db_backend.strip().lower()
    if backend != "qdrant":
        _fail(f"VECTOR_DB_BACKEND must be qdrant for this check (got: {backend!r})")


def _qdrant_client() -> tuple[QdrantClient, str]:
    settings = get_settings()
    url = ensure_qdrant_url(settings.qdrant_url)
    client = QdrantClient(url=url, api_key=settings.qdrant_api_key or None)
    return client, settings.qdrant_collection


def _require_indexed_collection() -> None:
    client, collection = _qdrant_client()
    if not client.collection_exists(collection):
        _fail(f"Collection {collection!r} not found. Run: make index (or .\\make.ps1 index)")
    count = client.count(collection_name=collection, exact=True).count
    if count == 0:
        _fail(f"Collection {collection!r} is empty. Run: make index (or .\\make.ps1 index)")
    _ok(f"Qdrant collection {collection!r} has {count} point(s)")


def _invoke_search(query: str, audience: str) -> list[dict[str, Any]]:
    raw = search_knowledge_base_tool.invoke({"query": query, "audience": audience})
    payload: Any = json.loads(raw)
    if isinstance(payload, dict) and "error" in payload:
        _fail(f"search_knowledge_base_tool error: {payload['error']}")
    if not isinstance(payload, list):
        _fail(f"unexpected tool payload type: {type(payload).__name__}")
    return payload


def _assert_hit_fields(hit: dict[str, Any], *, audience: str, source_prefix: str) -> None:
    for key in ("text", "source", "audience", "score"):
        if key not in hit:
            _fail(f"result missing field {key!r}: {hit}")
    if not str(hit["text"]).strip():
        _fail(f"empty text in result: {hit}")
    if hit["audience"] != audience:
        _fail(f"expected audience={audience!r}, got {hit['audience']!r} (source={hit['source']!r})")
    source = str(hit["source"])
    if not source.startswith(source_prefix):
        _fail(f"expected source prefix {source_prefix!r}, got {source!r}")
    if not isinstance(hit["score"], (int, float)):
        _fail(f"score must be numeric, got {hit['score']!r}")


def check_e2e(*, query: str) -> None:
    """Point 3: E2E search after index — b2c hit with text, source, audience, score."""
    _require_openrouter_key()
    _require_qdrant_backend()
    _require_indexed_collection()

    results = _invoke_search(query, "b2c")
    if not results:
        _fail(f"no results for query={query!r}, audience=b2c (run make index?)")

    for hit in results:
        _assert_hit_fields(hit, audience="b2c", source_prefix="b2c/")

    top = results[0]
    _ok(
        f"E2E search b2c: hits={len(results)}, top source={top['source']!r}, score={top['score']}",
    )


def check_audience_filter(*, query: str) -> None:
    """Point 4: same query, different audience — only matching source prefix."""
    _require_openrouter_key()
    _require_qdrant_backend()
    _require_indexed_collection()

    b2c_results = _invoke_search(query, "b2c")
    b2b_results = _invoke_search(query, "b2b")

    if not b2c_results:
        _fail(f"no b2c results for query={query!r} (try a broader query)")
    if not b2b_results:
        _fail(f"no b2b results for query={query!r} (try a broader query)")

    for hit in b2c_results:
        _assert_hit_fields(hit, audience="b2c", source_prefix="b2c/")
    for hit in b2b_results:
        _assert_hit_fields(hit, audience="b2b", source_prefix="b2b/")

    b2c_sources = {hit["source"] for hit in b2c_results}
    b2b_sources = {hit["source"] for hit in b2b_results}
    overlap = b2c_sources & b2b_sources
    if overlap:
        _fail(f"source overlap between b2c and b2b: {sorted(overlap)}")

    _ok(
        "audience filter: "
        f"b2c hits={len(b2c_results)} sources={sorted(b2c_sources)}, "
        f"b2b hits={len(b2b_results)} sources={sorted(b2b_sources)}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG search smoke checks (live Qdrant)")
    parser.add_argument(
        "command",
        choices=["e2e", "audience-filter"],
        help="e2e = point 3; audience-filter = point 4",
    )
    parser.add_argument(
        "--query",
        default="",
        help="override search query (default depends on command)",
    )
    args = parser.parse_args()

    _bootstrap_env()

    if args.command == "e2e":
        query = args.query or os.getenv("RAG_CHECK_B2C_QUERY", DEFAULT_B2C_QUERY)
        check_e2e(query=query)
        _ok("check-rag-search-e2e passed")
        return

    query = args.query or os.getenv("RAG_CHECK_FILTER_QUERY", DEFAULT_FILTER_QUERY)
    check_audience_filter(query=query)
    _ok("check-rag-audience-filter passed")


if __name__ == "__main__":
    main()
