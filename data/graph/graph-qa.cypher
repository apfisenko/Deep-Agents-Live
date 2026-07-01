// GraphRAG catalog QA — sprint-06 task 05 (parts b, c, g)
// Read-only diagnostics: make graph-qa / backend/app/graph/qa_cli.py

// ---------------------------------------------------------------------------
// 1. Node counts by label
// ---------------------------------------------------------------------------

MATCH (n)
RETURN labels(n)[0] AS label, count(*) AS nodes
ORDER BY nodes DESC;

// ---------------------------------------------------------------------------
// 2. Orphan modules (no incoming HAS_MODULE)
// ---------------------------------------------------------------------------

MATCH (m:Module)
WHERE NOT ()-[:HAS_MODULE]->(m)
RETURN m.courseSlug AS courseSlug, m.moduleNumber AS moduleNumber, m.title AS title
ORDER BY courseSlug, moduleNumber;

// ---------------------------------------------------------------------------
// 3. Orphan courses outside combo
// ---------------------------------------------------------------------------

MATCH (c:Course)
WHERE NOT (:Combo)-[:INCLUDES]->(c)
RETURN c.slug AS slug, c.name AS name;

// ---------------------------------------------------------------------------
// 4. Orphan themes (no incoming COVERS)
// ---------------------------------------------------------------------------

MATCH (t:Theme)
WHERE NOT ()-[:COVERS]->(t)
RETURN t.canonicalName AS theme
ORDER BY theme;

// ---------------------------------------------------------------------------
// 5. Duplicate Fullstack courses (entity resolution)
// ---------------------------------------------------------------------------

MATCH (c:Course)
WHERE c.slug CONTAINS 'fullstack' OR toLower(coalesce(c.name, '')) CONTAINS 'fullstack'
RETURN c.slug AS slug, c.name AS name, c.sourcePaths AS sourcePaths;

// ---------------------------------------------------------------------------
// 6. Legacy products.json slugs (should be empty)
// ---------------------------------------------------------------------------

MATCH (c:Course)
WHERE c.slug IN ['llm-start', 'deep-agents', 'aidd-program']
RETURN c.slug AS slug, c.priceRub AS priceRub;

// ---------------------------------------------------------------------------
// 7. Similar theme duplicates (APOC text similarity — Sorensen-Dice)
// ---------------------------------------------------------------------------

MATCH (a:Theme), (b:Theme)
WHERE elementId(a) < elementId(b)
  AND a.canonicalName IS :: STRING
  AND b.canonicalName IS :: STRING
WITH a, b, apoc.text.sorensenDiceSimilarity(a.canonicalName, b.canonicalName) AS similarity
WHERE similarity >= 0.6
RETURN a.canonicalName AS themeA, b.canonicalName AS themeB, round(similarity, 3) AS similarity
ORDER BY similarity DESC
LIMIT 25;

// ---------------------------------------------------------------------------
// 8. Degree distribution (all nodes with rels)
// ---------------------------------------------------------------------------

MATCH (n)
OPTIONAL MATCH (n)-[r]-()
WITH labels(n)[0] AS label, n, count(r) AS degree
RETURN label, coalesce(n.slug, n.canonicalName, n.name, toString(id(n))) AS nodeKey, degree
ORDER BY label, degree DESC;

// ---------------------------------------------------------------------------
// 9. Course COVERS coverage (% courses with at least one COVERS edge)
// ---------------------------------------------------------------------------

MATCH (c:Course)
OPTIONAL MATCH (c)-[:COVERS]->(t:Theme)
WITH count(c) AS totalCourses,
     count(CASE WHEN t IS NOT NULL THEN 1 END) AS coursesWithCovers
RETURN totalCourses,
       coursesWithCovers,
       round(100.0 * coursesWithCovers / totalCourses, 1) AS pctCoursesWithCovers;

// ---------------------------------------------------------------------------
// 10. Theme count per course
// ---------------------------------------------------------------------------

MATCH (c:Course)
OPTIONAL MATCH (c)-[:COVERS]->(t:Theme)
RETURN c.slug AS course, c.stepOrder AS stepOrder, count(DISTINCT t) AS themeCount
ORDER BY stepOrder;

// ---------------------------------------------------------------------------
// 11. Prerequisite chain (4 steps)
// ---------------------------------------------------------------------------

MATCH path = (start:Course {slug: 'ai-coding-intensive-cursor'})
             -[:RECOMMENDED_BEFORE*]->
             (end:Course {slug: 'deep-agents-advanced'})
RETURN [n IN nodes(path) | n.slug] AS chain, length(path) AS hops;

// ---------------------------------------------------------------------------
// 12. REQUIRES dangling (missing endpoint)
// ---------------------------------------------------------------------------

MATCH (a:Theme)-[r:REQUIRES]->(b:Theme)
WHERE b IS NULL
RETURN a.canonicalName AS fromTheme, type(r) AS rel;

// ---------------------------------------------------------------------------
// 13. GraphRAG eval path (M2)
// ---------------------------------------------------------------------------

MATCH (c:Course {slug: 'deep-agents-advanced'})-[:COVERS]->(t:Theme {canonicalName: 'GraphRAG'})
OPTIONAL MATCH (t)-[:REQUIRES]->(pre:Theme)
RETURN c.slug AS course, t.canonicalName AS theme, collect(pre.canonicalName) AS requires;

// ---------------------------------------------------------------------------
// 14. Lexical pipeline leftovers (should be empty after promote)
// ---------------------------------------------------------------------------

MATCH (n)
WHERE n:Document OR n:Chunk OR n:__Entity__ OR n:__KGBuilder__
RETURN labels(n)[0] AS label, count(*) AS nodes;
