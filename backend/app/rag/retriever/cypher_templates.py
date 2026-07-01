"""Cypher fragments for graph and global retrieval (schema.md §3)."""

from __future__ import annotations

# VectorCypher / QdrantNeo4j retrieval_query: ≤2 hops from anchor Course node.
GRAPH_RETRIEVAL_QUERY = """
OPTIONAL MATCH (node)-[:RECOMMENDED_BEFORE*1..2]->(later:Course)
OPTIONAL MATCH (node)-[:COVERS]->(t:Theme)
OPTIONAL MATCH (t)-[:REQUIRES*1..2]->(pre:Theme)
RETURN node.slug AS courseSlug,
       node.name AS courseName,
       node.priceRub AS priceRub,
       node.sourcePaths AS sourcePaths,
       [s IN collect(DISTINCT later.slug) WHERE s IS NOT NULL] AS laterCourses,
       [x IN collect(DISTINCT t.canonicalName) WHERE x IS NOT NULL] AS themes,
       [y IN collect(DISTINCT pre.canonicalName) WHERE y IS NOT NULL] AS themePrereqs,
       score
"""

COMBO_TRAJECTORY_QUERY = """
MATCH (combo:Combo {slug: $comboSlug})
MATCH (combo)-[inc:INCLUDES]->(c:Course)
OPTIONAL MATCH (c)-[:HAS_LEVEL]->(lvl:Level)
OPTIONAL MATCH (c)-[:HAS_FORMAT]->(fmt:Format)
OPTIONAL MATCH (c)-[:COVERS]->(t:Theme)
WITH combo, c, inc.order AS ord, lvl, fmt, collect(DISTINCT t.canonicalName) AS themes
ORDER BY ord
RETURN combo.name AS comboName,
       combo.priceRub AS comboPriceRub,
       collect({
         slug: c.slug,
         stepOrder: c.stepOrder,
         priceRub: c.priceRub,
         level: lvl.name,
         format: fmt.name,
         themes: themes
       }) AS trajectory
LIMIT 1
"""

CROSS_CUTTING_THEMES_QUERY = """
MATCH (:Combo {slug: $comboSlug})-[:INCLUDES]->(c:Course)
MATCH (c)-[:COVERS]->(t:Theme)
WITH t.canonicalName AS theme, count(DISTINCT c) AS n
WHERE n = 4
RETURN collect(theme) AS crossCuttingThemes
"""

AUDIENCE_MATRIX_QUERY = """
MATCH (:Combo {slug: $comboSlug})-[:INCLUDES]->(c:Course)
MATCH (c)-[:TARGETS]->(a:Audience)
RETURN c.slug AS courseSlug,
       c.stepOrder AS stepOrder,
       collect(a.name) AS audiences
ORDER BY c.stepOrder
"""

PREREQUISITE_CHAIN_QUERY = """
MATCH (:Combo {slug: $comboSlug})-[:INCLUDES]->(start:Course)
WHERE start.stepOrder = 1
MATCH path = (start)-[:RECOMMENDED_BEFORE*]->(end:Course)
WITH [n IN nodes(path) | n.slug] AS chain
RETURN chain
ORDER BY size(chain) DESC
LIMIT 1
"""
