"""OpenRouter vision-language caption client."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

from app.config import Settings, get_settings
from app.integrations.openrouter import _default_headers, map_openai_exception
from app.rag.caption.image import image_to_data_url
from app.rag.caption.pricing import estimate_vlm_cost_usd
from app.rag.caption.prompts import DEFAULT_CAPTION_PROMPT
from app.rag.caption.protocol import CaptionResult, CaptionUsage

logger = logging.getLogger(__name__)


class OpenRouterVlmCaptioner:
    model_id: str

    def __init__(self, model_id: str, settings: Settings | None = None) -> None:
        self.model_id = model_id
        self._settings = settings or get_settings()

    def caption_slide(
        self,
        image_path: Path,
        *,
        prompt: str | None = None,
        max_side: int = 1536,
    ) -> CaptionResult:
        text_prompt = prompt or DEFAULT_CAPTION_PROMPT
        data_url = image_to_data_url(image_path, max_side=max_side)
        payload = {
            "model": self.model_id,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
            **_default_headers(self._settings),
        }
        url = f"{self._settings.openrouter_base_url.rstrip('/')}/chat/completions"
        try:
            with httpx.Client(timeout=self._settings.llm_timeout_sec) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
        except Exception as exc:
            logger.warning(
                "VLM caption failed",
                extra={"model": self.model_id, "slide": str(image_path), "error": str(exc)},
            )
            raise map_openai_exception(exc) from exc

        usage_raw = body.get("usage") or {}
        usage = CaptionUsage(
            prompt_tokens=int(usage_raw.get("prompt_tokens") or 0),
            completion_tokens=int(usage_raw.get("completion_tokens") or 0),
            total_tokens=int(usage_raw.get("total_tokens") or 0),
        )
        est_cost = estimate_vlm_cost_usd(
            self.model_id,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
        )
        text = _extract_content(body)
        return CaptionResult(text=text, usage=usage, est_cost_usd=est_cost)


def _extract_content(body: dict) -> str:
    choices = body.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(part.strip() for part in parts if part.strip())
    return ""
