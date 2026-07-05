"""Jina v4 multivector embedding client (method D)."""

from __future__ import annotations

import base64
import io
import logging
import time
from pathlib import Path
from typing import Any

import httpx
from httpx import HTTPStatusError, ReadTimeout, WriteTimeout
from PIL import Image

from app.config import Settings, get_settings
from app.rag.caption.image import resize_for_vlm

logger = logging.getLogger(__name__)

JINA_EMBEDDINGS_URL = "https://api.jina.ai/v1/embeddings"
DEFAULT_JINA_MODEL = "jina-embeddings-v4"
DEFAULT_MULTIVECTOR_DIM = 128
EST_COST_PER_IMAGE_USD = 0.0001
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
IMAGE_FALLBACK_SIDES = (512, 384)


class JinaMultivectorEmbedder:
    model_id: str

    def __init__(self, model_id: str, settings: Settings | None = None) -> None:
        self.model_id = model_id
        self._settings = settings or get_settings()

    def embed_image(self, image_path: Path, *, max_side: int = 768) -> list[list[float]]:
        sides = _image_max_sides(max_side)
        last_error: Exception | None = None
        for idx, side in enumerate(sides):
            data_url = _image_to_jpeg_data_url(image_path, max_side=side)
            payload = {
                "model": self.model_id,
                "task": "retrieval.passage",
                "input": [{"image": data_url}],
                "return_multivector": True,
            }
            label = f"{image_path.name}@{side}"
            try:
                return self._request_multivector(payload, label=label, throttle=True)
            except RuntimeError as exc:
                last_error = exc
                if idx >= len(sides) - 1:
                    break
                logger.warning(
                    "Jina image embed retry with smaller max_side",
                    extra={"slide": image_path.name, "next_max_side": sides[idx + 1]},
                )
                time.sleep(self._settings.jina_request_delay_sec)
        msg = f"Jina image embed failed for {image_path.name}: {last_error}"
        raise RuntimeError(msg) from last_error

    def embed_query(self, text: str) -> list[list[float]]:
        payload = {
            "model": self.model_id,
            "task": "retrieval.query",
            "input": [text],
            "return_multivector": True,
        }
        return self._request_multivector(payload, label="query", throttle=False)

    def _request_multivector(
        self,
        payload: dict[str, Any],
        *,
        label: str,
        throttle: bool,
    ) -> list[list[float]]:
        api_key = self._settings.jina_api_key
        if not api_key:
            msg = "JINA_API_KEY is required for Jina multivector embeddings"
            raise RuntimeError(msg)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        timeout = httpx.Timeout(
            connect=15.0,
            read=float(self._settings.jina_embedding_timeout_sec),
            write=60.0,
            pool=15.0,
        )
        max_attempts = max(1, self._settings.jina_embedding_retries)
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(JINA_EMBEDDINGS_URL, headers=headers, json=payload)
                    response.raise_for_status()
                    body = response.json()
                if throttle and self._settings.jina_request_delay_sec > 0:
                    time.sleep(self._settings.jina_request_delay_sec)
                return _extract_multivector(body)
            except (ReadTimeout, WriteTimeout) as exc:
                last_error = exc
                logger.warning(
                    "Jina multivector timeout",
                    extra={"model": self.model_id, "label": label, "attempt": attempt},
                )
            except HTTPStatusError as exc:
                last_error = exc
                status = exc.response.status_code
                if status not in RETRYABLE_STATUS:
                    raise RuntimeError(str(exc)) from exc
                logger.warning(
                    "Jina multivector HTTP error",
                    extra={
                        "model": self.model_id,
                        "label": label,
                        "status": status,
                        "attempt": attempt,
                    },
                )
            except Exception as exc:
                logger.warning(
                    "Jina multivector embed failed",
                    extra={"model": self.model_id, "label": label, "error": str(exc)},
                )
                raise RuntimeError(str(exc)) from exc

            if attempt < max_attempts:
                multiplier = 5 if isinstance(last_error, HTTPStatusError) else 2
                sleep_s = min(2**attempt * multiplier, 60)
                time.sleep(sleep_s)

        msg = f"Jina multivector failed after {max_attempts} attempts ({label}): {last_error}"
        raise RuntimeError(msg) from last_error


def _image_max_sides(max_side: int) -> tuple[int, ...]:
    sides: list[int] = [max_side]
    for fallback in IMAGE_FALLBACK_SIDES:
        if fallback < max_side and fallback not in sides:
            sides.append(fallback)
    return tuple(sides)


def _image_to_jpeg_data_url(image_path: Path, *, max_side: int) -> str:
    with Image.open(image_path) as image:
        resized = resize_for_vlm(image, max_side=max_side)
        buffer = io.BytesIO()
        resized.save(buffer, format="JPEG", quality=85, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _extract_multivector(body: dict[str, Any]) -> list[list[float]]:
    data = body.get("data") or []
    if not data:
        msg = "Jina API returned empty data"
        raise RuntimeError(msg)
    first = data[0]
    raw = first.get("embeddings") or first.get("embedding")
    if raw is None:
        msg = "Jina API returned no multivector embeddings"
        raise RuntimeError(msg)
    if not raw:
        msg = "Jina API returned empty multivector"
        raise RuntimeError(msg)
    if isinstance(raw[0], (int, float)):
        return [[float(value) for value in raw]]
    vectors: list[list[float]] = []
    for row in raw:
        if not isinstance(row, list):
            msg = f"Unexpected multivector row type: {type(row)!r}"
            raise TypeError(msg)
        vectors.append([float(value) for value in row])
    return vectors
