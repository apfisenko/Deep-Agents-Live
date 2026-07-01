"""Entity resolution for Course and Theme nodes."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from neo4j import Driver, RoutingControl

from app.paths import GRAPH_THEME_ALIASES_YAML

logger = logging.getLogger(__name__)

_CANONICAL_FULLSTACK = "ai-driven-fullstack"
_LEGACY_COURSE_SLUGS = ["aidd-program", "llm-start", "deep-agents"]

_MERGE_THEME_ALIAS = """
MATCH (canon:Theme {canonicalName: $canonical})
MATCH (dup:Theme)
WHERE elementId(dup) <> elementId(canon)
  AND dup.canonicalName IS :: STRING
  AND (
    dup.canonicalName = $alias
    OR toLower(dup.canonicalName) = toLower($alias)
    OR $alias IN coalesce(dup.aliases, [])
  )
CALL apoc.refactor.mergeNodes([canon, dup], {properties: 'overwrite', mergeRels: true})
YIELD node
SET node.aliases = apoc.coll.toSet(coalesce(node.aliases, []) + [$alias])
RETURN node.canonicalName AS canonicalName
"""

_COURSE_GUARD = """
MATCH (canon:Course {slug: $canonicalSlug})
MATCH (dup:Course)
WHERE dup.slug <> $canonicalSlug
  AND dup.slug IS :: STRING
  AND (
    dup.slug IN $legacySlugs
    OR dup.slug CONTAINS 'fullstack'
    OR dup.slug CONTAINS 'aidd'
  )
SET canon.sourcePaths = apoc.coll.toSet(
  coalesce(canon.sourcePaths, []) + coalesce(dup.sourcePaths, [])
)
WITH dup, canon
OPTIONAL MATCH (dup)-[r:COVERS]->(t:Theme)
FOREACH (_ IN CASE WHEN r IS NULL THEN [] ELSE [1] END | MERGE (canon)-[:COVERS]->(t))
DELETE r
DETACH DELETE dup
"""

_DELETE_LEGACY_COURSES = """
MATCH (c:Course)
WHERE c.slug IN $legacySlugs
DETACH DELETE c
"""


def load_theme_aliases(path: Path | None = None) -> dict[str, list[str]]:
    """Load canonical theme name → alias list from YAML."""
    alias_path = path or GRAPH_THEME_ALIASES_YAML
    if not alias_path.is_file():
        return {}
    raw: dict[str, Any] = yaml.safe_load(alias_path.read_text(encoding="utf-8")) or {}
    return {str(k): [str(a) for a in v] if isinstance(v, list) else [] for k, v in raw.items()}


def sanitize_theme_nodes(driver: Driver, *, database: str) -> None:
    """Fix or remove Theme nodes where canonicalName is not a string."""
    records, _, _ = driver.execute_query(
        """
        MATCH (t:Theme)
        RETURN elementId(t) AS eid, t.canonicalName AS cn, coalesce(t.aliases, []) AS aliases
        """,
        database_=database,
        routing_=RoutingControl.READ,
    )
    fixed = 0
    for row in records:
        cn = row["cn"]
        if isinstance(cn, str):
            continue
        eid = row["eid"]
        aliases = row["aliases"] or []
        if isinstance(cn, list) and cn:
            first_name = str(cn[0])
            extra_aliases = [str(x) for x in cn[1:]]
        else:
            driver.execute_query(
                "MATCH (t:Theme) WHERE elementId(t) = $eid DETACH DELETE t",
                eid=eid,
                database_=database,
                routing_=RoutingControl.WRITE,
            )
            continue
        driver.execute_query(
            """
            MATCH (t:Theme) WHERE elementId(t) = $eid
            MERGE (canon:Theme {canonicalName: $firstName})
            ON CREATE SET canon.name = $firstName,
                          canon.aliases = apoc.coll.toSet($aliases + $extraAliases)
            ON MATCH SET canon.aliases = apoc.coll.toSet(
              coalesce(canon.aliases, []) + $aliases + $extraAliases
            )
            WITH t, canon
            OPTIONAL MATCH (src)-[r:COVERS]->(t)
            FOREACH (_ IN CASE WHEN r IS NULL THEN [] ELSE [1] END | MERGE (src)-[:COVERS]->(canon))
            DELETE r
            WITH t, canon
            OPTIONAL MATCH (t)-[r2:COVERS]->(tgt)
            FOREACH (_ IN CASE WHEN r2 IS NULL THEN [] ELSE [1] END | MERGE (canon)-[:COVERS]->(tgt))
            DELETE r2
            WITH t, canon
            OPTIONAL MATCH (t)-[r3:REQUIRES]->(pre)
            FOREACH (_ IN CASE WHEN r3 IS NULL THEN [] ELSE [1] END | MERGE (canon)-[:REQUIRES]->(pre))
            DELETE r3
            WITH t, canon
            OPTIONAL MATCH (post)-[r4:REQUIRES]->(t)
            FOREACH (_ IN CASE WHEN r4 IS NULL THEN [] ELSE [1] END | MERGE (post)-[:REQUIRES]->(canon))
            DELETE r4
            DETACH DELETE t
            """,
            eid=eid,
            firstName=first_name,
            aliases=aliases,
            extraAliases=extra_aliases,
            database_=database,
            routing_=RoutingControl.WRITE,
        )
        fixed += 1
    if fixed:
        logger.info("Sanitized %d Theme node(s) with non-string canonicalName", fixed)


def merge_theme_aliases(driver: Driver, *, database: str, aliases: dict[str, list[str]]) -> int:
    """Merge duplicate Theme nodes by alias map."""
    merged = 0
    for canonical, alias_list in aliases.items():
        driver.execute_query(
            """
            MERGE (t:Theme {canonicalName: $canonical})
            ON CREATE SET t.name = $canonical, t.aliases = []
            ON MATCH SET t.aliases = coalesce(t.aliases, [])
            """,
            canonical=canonical,
            database_=database,
            routing_=RoutingControl.WRITE,
        )
        for alias in alias_list:
            records, _, _ = driver.execute_query(
                _MERGE_THEME_ALIAS,
                canonical=canonical,
                alias=alias,
                database_=database,
                routing_=RoutingControl.WRITE,
            )
            if records:
                merged += 1
    return merged


def guard_course_duplicates(driver: Driver, *, database: str) -> None:
    """Ensure single canonical Fullstack course; remove legacy Course nodes."""
    driver.execute_query(
        _COURSE_GUARD,
        canonicalSlug=_CANONICAL_FULLSTACK,
        legacySlugs=_LEGACY_COURSE_SLUGS,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    driver.execute_query(
        _DELETE_LEGACY_COURSES,
        legacySlugs=_LEGACY_COURSE_SLUGS,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    logger.info("Course entity resolution: canonical slug=%s", _CANONICAL_FULLSTACK)


def _link_orphan_themes_from_requires(driver: Driver, *, database: str) -> None:
    """Link orphan REQUIRES-only themes to courses that cover their prerequisites."""
    driver.execute_query(
        """
        MATCH (orphan:Theme)
        WHERE NOT ()-[:COVERS]->(orphan)
        MATCH (orphan)-[:REQUIRES]->(pre:Theme)
        MATCH (c:Course)-[:COVERS]->(pre)
        MERGE (c)-[:COVERS]->(orphan)
        """,
        database_=database,
        routing_=RoutingControl.WRITE,
    )


def run_fuzzy_theme_resolution(driver: Driver, *, database: str, threshold: float = 0.88) -> None:
    """Fuzzy merge for remaining Theme duplicates (rapidfuzz).

    Skipped for catalog graph: FuzzyMatchResolver targets pipeline ``__Entity__`` nodes,
    while our indexed themes are native ``:Theme`` labels (alias YAML covers merges).
    """
    logger.info(
        "Skipping FuzzyMatchResolver for native :Theme catalog (threshold=%s unused)",
        threshold,
    )


def run_entity_resolution(driver: Driver, *, database: str) -> None:
    """Full entity resolution: sanitize + Course guard + alias merge + fuzzy pass."""
    from app.graph.theme_extractor import prune_orphan_themes

    sanitize_theme_nodes(driver, database=database)
    guard_course_duplicates(driver, database=database)
    aliases = load_theme_aliases()
    merged = merge_theme_aliases(driver, database=database, aliases=aliases)
    logger.info("Merged %d theme alias duplicate(s)", merged)
    run_fuzzy_theme_resolution(driver, database=database)
    _link_orphan_themes_from_requires(driver, database=database)
    prune_orphan_themes(driver, database=database)
