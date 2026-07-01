r"""Graph QA checks and graph-qa.cypher report (make graph-qa / .\make.ps1 graph-qa)."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from neo4j import Driver, RoutingControl
from neo4j.exceptions import Neo4jError

from app.config import clear_settings_cache, get_settings
from app.env_loader import load_repo_env
from app.exceptions import ProviderUnavailableError
from app.graph.client import create_driver, ensure_neo4j_uri
from app.graph.cypher_file import parse_cypher_file
from app.logging_config import configure_logging
from app.paths import GRAPH_QA_CYPHER

logger = logging.getLogger(__name__)

_SECTION_HEADER = re.compile(r"^//\s*-+\s*\n//\s*\d+\.\s*(.+?)\s*\n//\s*-+", re.MULTILINE)


@dataclass(frozen=True)
class GraphCheck:
    name: str
    query: str
    validate: Callable[[list[dict[str, Any]]], bool]
    expected: str


def _scalar(records: list[dict[str, Any]], key: str) -> Any:
    if not records:
        return None
    return records[0].get(key)


CHECKS: tuple[GraphCheck, ...] = (
    GraphCheck(
        name="combo_count",
        query="MATCH (cb:Combo) RETURN count(cb) AS n",
        validate=lambda r: _scalar(r, "n") == 1,
        expected="1 Combo node",
    ),
    GraphCheck(
        name="course_count",
        query="MATCH (c:Course) RETURN count(c) AS n",
        validate=lambda r: _scalar(r, "n") == 4,
        expected="4 Course nodes",
    ),
    GraphCheck(
        name="fullstack_single_course",
        query=("MATCH (c:Course) WHERE c.slug CONTAINS 'fullstack' RETURN count(c) AS n"),
        validate=lambda r: _scalar(r, "n") == 1,
        expected="1 canonical Fullstack Course",
    ),
    GraphCheck(
        name="legacy_products_excluded",
        query=(
            "MATCH (c:Course) WHERE c.slug IN ['llm-start', 'deep-agents', 'aidd-program'] "
            "RETURN count(c) AS n"
        ),
        validate=lambda r: _scalar(r, "n") == 0,
        expected="0 legacy courses",
    ),
    GraphCheck(
        name="prerequisite_chain",
        query=(
            "MATCH path = (start:Course {slug: 'ai-coding-intensive-cursor'})"
            "-[:RECOMMENDED_BEFORE*]->(end:Course {slug: 'deep-agents-advanced'}) "
            "RETURN length(path) AS hops"
        ),
        validate=lambda r: _scalar(r, "hops") == 3,
        expected="3-hop RECOMMENDED_BEFORE chain",
    ),
    GraphCheck(
        name="combo_includes_order",
        query=(
            "MATCH (:Combo {slug: 'ai-agents-combo'})-[i:INCLUDES]->(c:Course) "
            "RETURN collect(i.order) AS orders"
        ),
        validate=lambda r: sorted(_scalar(r, "orders") or []) == [1, 2, 3, 4],
        expected="INCLUDES orders [1,2,3,4]",
    ),
    GraphCheck(
        name="orphan_modules",
        query=("MATCH (m:Module) WHERE NOT ()-[:HAS_MODULE]->(m) RETURN count(m) AS n"),
        validate=lambda r: _scalar(r, "n") == 0,
        expected="0 orphan Module nodes",
    ),
    GraphCheck(
        name="orphan_courses",
        query=("MATCH (c:Course) WHERE NOT (:Combo)-[:INCLUDES]->(c) RETURN count(c) AS n"),
        validate=lambda r: _scalar(r, "n") == 0,
        expected="0 Course nodes outside combo",
    ),
    GraphCheck(
        name="orphan_themes",
        query=("MATCH (t:Theme) WHERE NOT ()-[:COVERS]->(t) RETURN count(t) AS n"),
        validate=lambda r: _scalar(r, "n") == 0,
        expected="0 orphan Theme nodes",
    ),
    GraphCheck(
        name="graphrag_covers",
        query=(
            "MATCH (c:Course {slug: 'deep-agents-advanced'})-[:COVERS]->"
            "(t:Theme {canonicalName: 'GraphRAG'}) RETURN count(t) AS n"
        ),
        validate=lambda r: (_scalar(r, "n") or 0) >= 1,
        expected="deep-agents-advanced COVERS GraphRAG",
    ),
    GraphCheck(
        name="no_lexical_leftovers",
        query=(
            "MATCH (n) WHERE n:Document OR n:Chunk OR n:__Entity__ OR n:__KGBuilder__ "
            "RETURN count(n) AS n"
        ),
        validate=lambda r: _scalar(r, "n") == 0,
        expected="0 Document/Chunk pipeline nodes",
    ),
    GraphCheck(
        name="courses_with_covers_pct",
        query=(
            "MATCH (c:Course) OPTIONAL MATCH (c)-[:COVERS]->(t:Theme) "
            "WITH c, count(t) AS tc RETURN "
            "count(c) AS total, sum(CASE WHEN tc > 0 THEN 1 ELSE 0 END) AS withCovers"
        ),
        validate=lambda r: (_scalar(r, "total") or 0) > 0
        and (_scalar(r, "withCovers") or 0) == (_scalar(r, "total") or 0),
        expected="100% courses have COVERS",
    ),
)


def _section_titles(cypher_text: str, statement_count: int) -> list[str]:
    titles = [m.group(1).strip() for m in _SECTION_HEADER.finditer(cypher_text)]
    while len(titles) < statement_count:
        titles.append(f"Query {len(titles) + 1}")
    return titles


def _run_check(driver: Driver, *, database: str, check: GraphCheck) -> tuple[bool, Any]:
    records, _, _ = driver.execute_query(
        check.query,
        database_=database,
        routing_=RoutingControl.READ,
    )
    rows = [record.data() for record in records]
    ok = check.validate(rows)
    value = rows[0] if rows else {}
    return ok, value


def run_cypher_report(driver: Driver, *, database: str) -> None:
    """Execute graph-qa.cypher and print a human-readable report."""
    if not GRAPH_QA_CYPHER.is_file():
        print(f"QA file not found: {GRAPH_QA_CYPHER}", file=sys.stderr)
        return

    cypher_text = GRAPH_QA_CYPHER.read_text(encoding="utf-8")
    statements = parse_cypher_file(GRAPH_QA_CYPHER)
    titles = _section_titles(cypher_text, len(statements))

    print("=== graph-qa.cypher report ===\n")
    for idx, (title, statement) in enumerate(zip(titles, statements, strict=False)):
        print(f"--- {idx + 1}. {title} ---")
        try:
            records, _, _ = driver.execute_query(
                statement,
                database_=database,
                routing_=RoutingControl.READ,
            )
        except Neo4jError as exc:
            print(f"  ERROR: {exc.message}\n")
            continue
        rows = [record.data() for record in records]
        if not rows:
            print("  (empty)\n")
            continue
        for row in rows[:15]:
            print(f"  {row}")
        if len(rows) > 15:
            print(f"  ... ({len(rows) - 15} more rows)")
        print()


def run_checks(*, database: str) -> tuple[int, list[str]]:
    settings = get_settings()
    if not settings.neo4j_password.strip():
        msg = "NEO4J_PASSWORD is required (set in .env)"
        raise ProviderUnavailableError(message=msg, error_code="neo4j_config")

    uri = ensure_neo4j_uri(settings.neo4j_uri)
    driver = create_driver(uri, settings.neo4j_user, settings.neo4j_password)
    failures: list[str] = []
    try:
        driver.verify_connectivity()
        print("=== automated gates ===\n")
        for check in CHECKS:
            ok, value = _run_check(driver, database=database, check=check)
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {check.name}: expected {check.expected}; got {value}")
            if not ok:
                failures.append(check.name)

        print()
        run_cypher_report(driver, database=database)
    finally:
        driver.close()

    return (1 if failures else 0), failures


def _bootstrap_env() -> None:
    load_repo_env()
    clear_settings_cache()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run graph catalog QA checks and report")
    parser.add_argument(
        "--gates-only",
        action="store_true",
        help="Run automated gates only (skip graph-qa.cypher report)",
    )
    args = parser.parse_args()

    _bootstrap_env()
    settings = get_settings()
    configure_logging(settings.log_level, env=settings.env)

    try:
        if args.gates_only:
            uri = ensure_neo4j_uri(settings.neo4j_uri)
            driver = create_driver(uri, settings.neo4j_user, settings.neo4j_password)
            failures: list[str] = []
            try:
                driver.verify_connectivity()
                for check in CHECKS:
                    ok, value = _run_check(driver, database=settings.neo4j_database, check=check)
                    status = "PASS" if ok else "FAIL"
                    print(f"[{status}] {check.name}: expected {check.expected}; got {value}")
                    if not ok:
                        failures.append(check.name)
            finally:
                driver.close()
            if failures:
                print(f"\nGraph QA failed: {', '.join(failures)}", file=sys.stderr)
                return 1
            print("\nGraph QA: all gates passed")
            return 0

        exit_code, failures = run_checks(database=settings.neo4j_database)
        if failures:
            print(f"Graph QA failed gates: {', '.join(failures)}", file=sys.stderr)
            return exit_code
        print("Graph QA: all gates passed")
        return 0
    except ProviderUnavailableError as exc:
        logger.error("%s", exc.message)
        return 1
    except Exception:
        logger.exception("Graph QA failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
