"""Guarded Text2Cypher execution (guardrails #1-#3 + Text2CypherRetriever)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from neo4j import Driver, RoutingControl
from neo4j_graphrag.generation.prompts import Text2CypherTemplate
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers.text2cypher import extract_cypher

from app.config import Settings
from app.graph.client import get_text2cypher_driver
from app.rag.text2cypher.examples import get_few_shot_examples
from app.rag.text2cypher.guardrails import prepare_cypher
from app.rag.text2cypher.schema_loader import load_enhanced_schema_text

logger = logging.getLogger(__name__)

READ_ONLY_QUERY_TYPE = "r"


@dataclass(frozen=True)
class GuardedQueryResult:
    """Result of a guarded text2cypher query."""

    cypher: str
    rows: list[dict[str, Any]]


def _build_llm(settings: Settings) -> OpenAILLM:
    return OpenAILLM(
        model_name=settings.text2cypher_model,
        model_params={"temperature": 0},
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


def _records_to_rows(records: list[Any]) -> list[dict[str, Any]]:
    return [dict(record) for record in records]


class GuardedText2CypherExecutor:
    """NL→Cypher with readonly driver and application guardrails."""

    def __init__(
        self,
        settings: Settings,
        *,
        driver: Driver | None = None,
        llm: OpenAILLM | None = None,
    ) -> None:
        if not settings.neo4j_readonly_password:
            msg = (
                "NEO4J_READONLY_PASSWORD is required for text2cypher "
                "(Guardrail #1: readonly credentials only)"
            )
            raise ValueError(msg)
        self._settings = settings
        self._driver = driver or get_text2cypher_driver(settings)
        self._llm = llm or _build_llm(settings)
        self._schema = load_enhanced_schema_text()
        self._examples = get_few_shot_examples()
        self._timeout_sec = settings.text2cypher_query_timeout_ms / 1000.0
        self._default_limit = settings.text2cypher_default_limit

    def generate_cypher(self, query_text: str) -> str:
        """Generate Cypher from natural language via LLM."""
        prompt_template = Text2CypherTemplate()
        prompt = prompt_template.format(
            schema=self._schema,
            examples="\n".join(self._examples),
            query_text=query_text,
        )
        llm_result = self._llm.invoke(prompt)
        return extract_cypher(llm_result.content)

    def execute_prepared(self, cypher: str) -> GuardedQueryResult:
        """Run guardrails and execute read-only Cypher on Neo4j."""
        prepared = prepare_cypher(cypher, default_limit=self._default_limit)
        self._assert_read_only_explain(prepared)
        records, _, _ = self._driver.execute_query(
            query_=prepared,
            database_=self._settings.neo4j_database,
            routing_=RoutingControl.READ,
            timeout=self._timeout_sec,
        )
        rows = _records_to_rows(records)
        return GuardedQueryResult(cypher=prepared, rows=rows)

    def query(self, query_text: str) -> GuardedQueryResult:
        """Full pipeline: NL → Cypher → guardrails → execute."""
        raw_cypher = self.generate_cypher(query_text)
        return self.execute_prepared(raw_cypher)

    def _assert_read_only_explain(self, cypher: str) -> None:
        """Defense in depth: EXPLAIN must classify query as read-only."""
        _, explain_summary, _ = self._driver.execute_query(
            query_=f"EXPLAIN {cypher}",
            database_=self._settings.neo4j_database,
            routing_=RoutingControl.READ,
            timeout=self._timeout_sec,
        )
        if explain_summary.query_type != READ_ONLY_QUERY_TYPE:
            msg = f"Forbidden: non-read-only Cypher (query_type={explain_summary.query_type!r})"
            raise ValueError(msg)


def rows_to_chunk_text(rows: list[dict[str, Any]]) -> str:
    return json.dumps(rows, ensure_ascii=False)
