"""GraphSchema for schema-guided theme extraction (Course + Theme only)."""

from __future__ import annotations

from neo4j_graphrag.experimental.components.schema import (
    GraphSchema,
    NodeType,
    PropertyType,
    RelationshipType,
)

STRICT_EXTRACTION_INSTRUCTION = (
    "Extract ONLY technology/methodology concepts (RAG, GraphRAG, MCP, Observability). "
    "Do NOT extract lesson titles like 'Тема 5', people, prices, or generic words. "
    "Use canonicalName as the short canonical concept label. "
    "Course nodes must use existing slug from metadata — do not invent new courses."
)


def build_extraction_schema(*, strict: bool) -> GraphSchema:
    """Build GraphSchema with allowed labels Course, Theme and rels COVERS, REQUIRES."""
    course_desc = "B2C program step already in catalog; identify by slug property."
    theme_desc = "Cross-cutting technology or methodology concept in the course catalog."
    if strict:
        course_desc = f"{course_desc} {STRICT_EXTRACTION_INSTRUCTION}"
        theme_desc = f"{theme_desc} {STRICT_EXTRACTION_INSTRUCTION}"

    return GraphSchema(
        node_types=[
            NodeType(
                label="Course",
                description=course_desc,
                properties=[
                    PropertyType(name="slug", type="STRING"),
                    PropertyType(name="name", type="STRING"),
                ],
            ),
            NodeType(
                label="Theme",
                description=theme_desc,
                properties=[
                    PropertyType(name="canonicalName", type="STRING"),
                    PropertyType(name="name", type="STRING"),
                    PropertyType(name="aliases", type="LIST"),
                    PropertyType(name="context", type="STRING"),
                ],
            ),
        ],
        relationship_types=[
            RelationshipType(
                label="COVERS",
                description="Course covers a technology/methodology theme.",
            ),
            RelationshipType(
                label="REQUIRES",
                description="Theme requires another theme as prerequisite.",
                properties=[PropertyType(name="strength", type="STRING")],
            ),
        ],
        patterns=[
            ("Course", "COVERS", "Theme"),
            ("Theme", "REQUIRES", "Theme"),
        ],
    )
