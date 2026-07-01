r"""Offline RAG indexing CLI (make index / .\make.ps1 index)."""

from __future__ import annotations

import argparse
import logging
import sys

from app.config import get_settings
from app.exceptions import AgentCoreError
from app.logging_config import configure_logging
from app.rag.indexer import RagIndexer


def main() -> int:
    parser = argparse.ArgumentParser(description="Index knowledge base files into vector DB")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-index all files regardless of manifest hash",
    )
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level, env=settings.env)

    indexer = RagIndexer()
    try:
        result = indexer.build(force=args.force)
    except AgentCoreError as exc:
        logging.getLogger(__name__).error("%s", exc.message)  # noqa: TRY400
        return 1
    logging.getLogger(__name__).info(
        "Indexed %s file(s), %s chunk(s); skipped=%s failed=%s removed=%s",
        result.indexed,
        result.chunks,
        result.skipped,
        result.failed,
        result.removed,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
