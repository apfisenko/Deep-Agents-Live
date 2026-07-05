"""VLM captioning for multimodal RAG indexing."""

from app.rag.caption.batch import CaptionBatchMeta, run_caption_batch
from app.rag.caption.openrouter_vlm import OpenRouterVlmCaptioner
from app.rag.caption.prompts import DEFAULT_CAPTION_PROMPT

__all__ = [
    "DEFAULT_CAPTION_PROMPT",
    "CaptionBatchMeta",
    "OpenRouterVlmCaptioner",
    "run_caption_batch",
]
