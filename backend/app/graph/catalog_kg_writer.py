"""Neo4jWriter hook that MERGEs seed catalog Course/Theme nodes during KG extraction."""

from __future__ import annotations

import logging
from typing import Any

from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.components.types import LexicalGraphConfig, Neo4jNode

logger = logging.getLogger(__name__)

_MERGE_COURSE_NODES = """
UNWIND $rows AS row
MATCH (n:Course {slug: row.slug})
SET n.__tmp_internal_id = row.id
SET n:__KGBuilder__
"""

_MERGE_THEME_NODES = """
UNWIND $rows AS row
MERGE (n:Theme {canonicalName: row.canonicalName})
ON CREATE SET
  n.name = row.name,
  n.aliases = row.aliases
ON MATCH SET
  n.name = coalesce(n.name, row.name),
  n.aliases = coalesce(n.aliases, row.aliases)
SET n.__tmp_internal_id = row.id
SET n:__KGBuilder__
"""


def split_catalog_nodes(
    nodes: list[Neo4jNode],
) -> tuple[list[Neo4jNode], list[Neo4jNode], list[Neo4jNode]]:
    """Split extracted nodes into catalog Course, catalog Theme, and pipeline nodes."""
    courses: list[Neo4jNode] = []
    themes: list[Neo4jNode] = []
    other: list[Neo4jNode] = []
    for node in nodes:
        if node.label == "Course":
            courses.append(node)
        elif node.label == "Theme":
            themes.append(node)
        else:
            other.append(node)
    return courses, themes, other


def _course_rows(nodes: list[Neo4jNode]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in nodes:
        slug = node.properties.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            logger.warning("Skipping Course node without slug (id=%s)", node.id)
            continue
        rows.append({"id": node.id, "slug": slug})
    return rows


def _theme_rows(nodes: list[Neo4jNode]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in nodes:
        canonical = node.properties.get("canonicalName")
        if not isinstance(canonical, str) or not canonical.strip():
            name = node.properties.get("name")
            if isinstance(name, str) and name.strip():
                canonical = name
            else:
                logger.warning("Skipping Theme node without canonicalName (id=%s)", node.id)
                continue
        aliases = node.properties.get("aliases")
        if not isinstance(aliases, list):
            aliases = []
        display_name = node.properties.get("name")
        if not isinstance(display_name, str) or not display_name.strip():
            display_name = canonical
        rows.append(
            {
                "id": node.id,
                "canonicalName": canonical,
                "name": display_name,
                "aliases": [str(a) for a in aliases],
            },
        )
    return rows


def _catalog_upsert_nodes(
    writer: Neo4jWriter,
    original_upsert: Any,
    nodes: list[Neo4jNode],
    lexical_graph_config: LexicalGraphConfig,
) -> None:
    courses, themes, other = split_catalog_nodes(nodes)
    course_rows = _course_rows(courses)
    if course_rows:
        writer.driver.execute_query(
            _MERGE_COURSE_NODES,
            parameters_={"rows": course_rows},
            database_=writer.neo4j_database,
        )
    theme_rows = _theme_rows(themes)
    if theme_rows:
        writer.driver.execute_query(
            _MERGE_THEME_NODES,
            parameters_={"rows": theme_rows},
            database_=writer.neo4j_database,
        )
    if other:
        original_upsert(other, lexical_graph_config)


def build_catalog_kg_writer(driver: Any, *, neo4j_database: str) -> Neo4jWriter:
    """Return Neo4jWriter that MERGEs catalog Course/Theme instead of CREATE."""
    writer = Neo4jWriter(driver=driver, neo4j_database=neo4j_database)
    original_upsert = writer._upsert_nodes  # noqa: SLF001

    def upsert_nodes(
        nodes: list[Neo4jNode],
        lexical_graph_config: LexicalGraphConfig,
    ) -> None:
        _catalog_upsert_nodes(writer, original_upsert, nodes, lexical_graph_config)

    writer._upsert_nodes = upsert_nodes  # noqa: SLF001
    return writer
