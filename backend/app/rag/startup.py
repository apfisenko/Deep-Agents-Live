"""RAG startup checks (no indexing — use make index / index_cli)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.exceptions import ProviderUnavailableError
from app.rag.vector_store import get_vector_index_store

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)


def verify_rag_backend_on_startup(settings: Settings) -> None:
    """Log vector backend and optionally verify Qdrant is reachable."""
    backend = settings.vector_db_backend.strip().lower()
    logger.info(
        "RAG read path ready (offline index: make index)",
        extra={"vector_db_backend": backend},
    )
    if backend != "qdrant":
        return

    store = get_vector_index_store(settings)
    ensure_connection = getattr(store, "ensure_connection", None)
    if ensure_connection is None:
        return

    try:
        ensure_connection()
    except ProviderUnavailableError:
        logger.warning(
            "Qdrant unreachable at startup; run make up && make index before RAG search",
            exc_info=True,
        )
        return

    if store.is_empty():
        logger.warning(
            "Qdrant collection is empty; run make index (or .\\make.ps1 index) before RAG search",
        )
