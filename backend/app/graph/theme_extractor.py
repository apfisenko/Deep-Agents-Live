"""Schema-guided theme extraction via neo4j-graphrag SimpleKGPipeline."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

from neo4j import Driver, RoutingControl
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm import OpenAILLM

from app.config import Settings
from app.graph.catalog_kg_writer import build_catalog_kg_writer
from app.graph.cypher_file import run_cypher_file
from app.graph.extraction_schema import build_extraction_schema
from app.graph.noop_embedder import NoOpEmbedder
from app.graph.section_splitter import ProgramSectionSplitter
from app.graph.theme_baseline import apply_course_theme_baseline
from app.graph.theme_promoter import promote_and_cleanup
from app.paths import B2C_PROGRAMS_DIR, GRAPH_THEME_REQUIRES_CYPHER, REPO_ROOT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExtractionSource:
    course_slug: str
    relative_path: str
    legacy: bool = False


EXTRACTION_SOURCES: tuple[ExtractionSource, ...] = (
    ExtractionSource("ai-coding-intensive-cursor", "ai-coding-intensive-cursor.md"),
    ExtractionSource("ai-driven-fullstack", "ai-driven-fullstack.md"),
    ExtractionSource("ai-coding-agents-base", "ai-coding-agents-base.md"),
    ExtractionSource("deep-agents-advanced", "deep-agents-advanced.md"),
    ExtractionSource("ai-driven-fullstack", "aidd-program.md", legacy=True),
)


def _build_llm(settings: Settings) -> OpenAILLM:
    return OpenAILLM(
        model_name=settings.graph_extract_model,
        model_params={"temperature": 0},
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


def _build_pipeline(
    settings: Settings,
    driver: Driver,
) -> SimpleKGPipeline:
    if settings.graph_extract_strict:
        logger.info("GRAPH_EXTRACT_STRICT=true: schema enforced via GraphSchema")
    return SimpleKGPipeline(
        llm=_build_llm(settings),
        driver=driver,
        embedder=NoOpEmbedder(),
        schema=build_extraction_schema(strict=settings.graph_extract_strict),
        from_file=True,
        text_splitter=ProgramSectionSplitter(),
        perform_entity_resolution=False,
        kg_writer=build_catalog_kg_writer(driver, neo4j_database=settings.neo4j_database),
        on_error="IGNORE",
        neo4j_database=settings.neo4j_database,
    )


async def _extract_file(
    pipeline: SimpleKGPipeline,
    *,
    file_path: Path,
    course_slug: str,
    legacy: bool,
) -> None:
    metadata = {
        "courseSlug": course_slug,
        "sourcePath": str(file_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "legacy": "true" if legacy else "false",
    }
    await pipeline.run_async(
        file_path=str(file_path),
        document_metadata=metadata,
    )


def prune_orphan_themes(driver: Driver, *, database: str) -> int:
    """Remove Theme nodes with no incoming COVERS (LLM noise not linked to a course)."""
    _, summary, _ = driver.execute_query(
        """
        MATCH (t:Theme)
        WHERE NOT ()-[:COVERS]->(t)
        DETACH DELETE t
        """,
        database_=database,
        routing_=RoutingControl.WRITE,
    )
    deleted = 0
    if summary is not None and summary.counters is not None:
        deleted = summary.counters.nodes_deleted
    if deleted:
        logger.info("Pruned %d orphan Theme node(s) without COVERS", deleted)
    return deleted


def apply_theme_requires(driver: Driver, *, database: str) -> int:
    """Apply baseline REQUIRES edges from theme_requires.cypher."""
    if not GRAPH_THEME_REQUIRES_CYPHER.is_file():
        logger.warning("Missing %s — skipping REQUIRES baseline", GRAPH_THEME_REQUIRES_CYPHER)
        return 0
    return run_cypher_file(driver, GRAPH_THEME_REQUIRES_CYPHER, database=database, write=True)


def run_extraction(driver: Driver, settings: Settings) -> None:
    """Run SimpleKGPipeline extraction, then baseline MERGE + REQUIRES seed."""
    database = settings.neo4j_database
    pipeline = _build_pipeline(settings, driver)

    async def _run_all() -> None:
        for source in EXTRACTION_SOURCES:
            file_path = B2C_PROGRAMS_DIR / source.relative_path
            if not file_path.is_file():
                msg = f"Extraction source not found: {file_path}"
                raise FileNotFoundError(msg)
            logger.info("Extracting themes from %s (course=%s)", file_path.name, source.course_slug)
            await _extract_file(
                pipeline,
                file_path=file_path,
                course_slug=source.course_slug,
                legacy=source.legacy,
            )
            promote_and_cleanup(driver, database=database, course_slug=source.course_slug)

    asyncio.run(_run_all())
    apply_course_theme_baseline(driver, database=database)
    apply_theme_requires(driver, database=database)
    prune_orphan_themes(driver, database=database)
    logger.info("Theme extraction complete")
