"""Admin endpoints (dev only)."""

import asyncio

from fastapi import APIRouter, HTTPException

from app.api.schemas.chat import ReindexResponse
from app.config import get_settings
from app.rag.indexer import get_indexer

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reindex")
async def reindex() -> ReindexResponse:
    if get_settings().env != "dev":
        raise HTTPException(status_code=404, detail="Not Found")

    indexer = get_indexer()
    result = await asyncio.to_thread(indexer.build, force=True)
    return ReindexResponse(
        indexed=result.indexed,
        skipped=result.skipped,
        removed=result.removed,
    )
