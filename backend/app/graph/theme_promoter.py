"""Promote SimpleKGPipeline output into catalog Theme/Course COVERS and cleanup lexical layer."""

from __future__ import annotations

import logging

from neo4j import Driver, RoutingControl

logger = logging.getLogger(__name__)

_LEGACY_COURSE_SLUGS = ["aidd-program", "llm-start", "deep-agents"]

_PROMOTE_THEMES_FOR_COURSE = """
MATCH (seed:Course {slug: $courseSlug})
OPTIONAL MATCH (d:Document)
WHERE d.courseSlug = $courseSlug
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(ch:Chunk)
OPTIONAL MATCH (ch)-[:FROM_CHUNK]-(t:Theme)
WHERE t.canonicalName IS NOT NULL
WITH seed, collect(DISTINCT t) AS themes
UNWIND themes AS theme
MERGE (seed)-[:COVERS]->(theme)
"""

_NORMALIZE_THEMES = """
MATCH (t:Theme)
WHERE t.canonicalName IS NOT NULL
SET t.name = coalesce(t.name, t.canonicalName),
    t.aliases = coalesce(t.aliases, [])
"""

_REDIRECT_STRAY_COURSE_COVERS = """
MATCH (seed:Course {slug: $courseSlug})
MATCH (extra:Course)
WHERE extra.slug <> $courseSlug
  AND (
    extra.slug IN $legacySlugs
    OR NOT exists((:Combo)-[:INCLUDES]->(extra))
  )
OPTIONAL MATCH (extra)-[r:COVERS]->(t:Theme)
FOREACH (_ IN CASE WHEN r IS NULL THEN [] ELSE [1] END | MERGE (seed)-[:COVERS]->(t))
DELETE r
WITH extra
DETACH DELETE extra
"""

_STRIP_PIPELINE_LABELS = """
MATCH (n)
WHERE n:Theme OR n:Course
REMOVE n:__Entity__, n:__KGBuilder__
REMOVE n.__tmp_internal_id
"""

_CLEANUP_LEXICAL = """
MATCH (n)
WHERE (n:Document OR n:Chunk OR n:__Entity__ OR n:__KGBuilder__)
  AND NOT n:Theme AND NOT n:Course
DETACH DELETE n
"""


def promote_and_cleanup(driver: Driver, *, database: str, course_slug: str) -> None:
    """Merge extracted themes into seed Course and remove pipeline artifacts."""
    driver.execute_query(
        _NORMALIZE_THEMES,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    driver.execute_query(
        _PROMOTE_THEMES_FOR_COURSE,
        courseSlug=course_slug,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    driver.execute_query(
        _REDIRECT_STRAY_COURSE_COVERS,
        courseSlug=course_slug,
        legacySlugs=_LEGACY_COURSE_SLUGS,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    driver.execute_query(
        _STRIP_PIPELINE_LABELS,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    driver.execute_query(
        _CLEANUP_LEXICAL,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    logger.info("Promoted extraction for course %s and cleaned lexical layer", course_slug)
