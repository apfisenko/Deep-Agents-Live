#!/usr/bin/env python3
"""Smoke script for text2cypher guardrails and NL queries."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import clear_settings_cache, get_settings
from app.env_loader import load_repo_env
from app.rag.text2cypher.executor import GuardedText2CypherExecutor

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SMOKE_QUESTIONS: tuple[str, ...] = (
    "Сколько курсов входит в комбо ai-agents-combo?",
    "Сколько стоит комбо «ИИ-агенты», какая сумма курсов по отдельности и какой процент скидки?",
)


def _bootstrap_env() -> None:
    load_repo_env()
    clear_settings_cache()


def main() -> int:
    _bootstrap_env()
    settings = get_settings()
    if not settings.neo4j_readonly_password:
        logger.error("NEO4J_READONLY_PASSWORD is not set")
        return 1

    executor = GuardedText2CypherExecutor(settings)
    total = len(SMOKE_QUESTIONS)
    failures = 0

    for index, question in enumerate(SMOKE_QUESTIONS, start=1):
        logger.info("[smoke %d/%d] question: %s", index, total, question[:80])
        try:
            result = executor.query(question)
        except Exception:
            logger.exception("[smoke %d/%d] FAIL", index, total)
            failures += 1
            continue
        logger.info(
            "[smoke %d/%d] cypher: %s | rows=%d",
            index,
            total,
            result.cypher[:120],
            len(result.rows),
        )
        if not result.rows:
            logger.error("[smoke %d/%d] FAIL: empty rows", index, total)
            failures += 1

    if failures:
        logger.error("Smoke finished with %d failure(s) out of %d", failures, total)
        return 1
    logger.info("Smoke OK: %d/%d passed", total - failures, total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
