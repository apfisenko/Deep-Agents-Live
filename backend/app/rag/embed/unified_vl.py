"""OpenRouter unified vision-language embedding client (method C)."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

from app.config import Settings, get_settings
from app.integrations.openrouter import _default_headers, map_openai_exception
from app.rag.caption.image import image_to_data_url

logger = logging.getLogger(__name__)

DEFAULT_UNIFIED_EMBED_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"


class OpenRouterUnifiedEmbedder:
    model_id: str

    def __init__(self, model_id: str, settings: Settings | None = None) -> None:
        self.model_id = model_id
        self._settings = settings or get_settings()

    def embed_image(self, image_path: Path, *, max_side: int = 1536) -> list[float]:
        data_url = image_to_data_url(image_path, max_side=max_side)
        payload = {
            "model": self.model_id,
            "input": [
                {
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            "encoding_format": "float",
        }
        return self._request_embedding(payload)

    def embed_query(self, text: str) -> list[float]:
        payload = {
            "model": self.model_id,
            "input": [
                {
                    "content": [
                        {"type": "text", "text": text},
                    ],
                },
            ],
            "encoding_format": "float",
        }
        return self._request_embedding(payload)

    def _request_embedding(self, payload: dict) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
            **_default_headers(self._settings),
        }
        url = f"{self._settings.openrouter_base_url.rstrip('/')}/embeddings"
        try:
            with httpx.Client(timeout=self._settings.embedding_timeout_sec) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
        except Exception as exc:
            logger.warning(
                "Unified VL embed failed",
                extra={"model": self.model_id, "error": str(exc)},
            )
            raise map_openai_exception(exc) from exc
        return _extract_embedding(body)


def _extract_embedding(body: dict) -> list[float]:
    data = body.get("data") or []
    if not data:
        msg = "Embedding API returned empty data"
        raise RuntimeError(msg)
    first = data[0]
    embedding = first.get("embedding")
    if not isinstance(embedding, list) or not embedding:
        msg = "Embedding API returned invalid embedding vector"
        raise RuntimeError(msg)
    return [float(value) for value in embedding]
