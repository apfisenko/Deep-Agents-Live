"""Multimodal embedding clients for sprint-07 methods C and D."""

from app.rag.embed.jina_multivector import JinaMultivectorEmbedder
from app.rag.embed.unified_vl import OpenRouterUnifiedEmbedder

__all__ = ["JinaMultivectorEmbedder", "OpenRouterUnifiedEmbedder"]
