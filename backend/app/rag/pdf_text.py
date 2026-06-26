"""Extract text from PDF files (text layer, OCR, optional LLM fallback)."""

from __future__ import annotations

import base64
import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import fitz
import httpx

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)

_WHITESPACE_RE = re.compile(r"[ \t]+\n")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def extract_pdf_text(file_path: Path, settings: Settings) -> str:
    """Return normalized text from a PDF, using cache and sidecar overrides."""
    sidecar = file_path.with_suffix(f"{file_path.suffix}.extracted.txt")
    if sidecar.is_file():
        return _normalize_text(sidecar.read_text(encoding="utf-8"))

    cache_path = _cache_path(file_path)
    if cache_path.is_file():
        return _normalize_text(cache_path.read_text(encoding="utf-8"))

    doc = fitz.open(file_path)
    try:
        page_texts: list[str] = []
        for page in doc:
            text = _extract_page_text(page, settings)
            page_texts.append(text)
    finally:
        doc.close()

    combined = _normalize_text("\n\n".join(part for part in page_texts if part))
    if len(combined) >= settings.pdf_ocr_min_chars:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(combined, encoding="utf-8")
    return combined


def _extract_page_text(page: fitz.Page, settings: Settings) -> str:
    text = page.get_text().strip()
    if len(text) >= settings.pdf_ocr_min_chars:
        return text
    if not settings.pdf_ocr_enabled:
        return text

    ocr_text = _ocr_page_tesseract(page, settings)
    if len(ocr_text) >= settings.pdf_ocr_min_chars:
        return ocr_text

    if settings.pdf_ocr_llm_fallback:
        llm_text = _ocr_page_llm(page, settings)
        if len(llm_text) >= settings.pdf_ocr_min_chars:
            return llm_text

    return ocr_text or text


def _ocr_page_tesseract(page: fitz.Page, settings: Settings) -> str:
    try:
        textpage = page.get_textpage_ocr(
            language=settings.pdf_ocr_language,
            dpi=settings.pdf_ocr_dpi,
            full=True,
        )
        return page.get_text(textpage=textpage).strip()
    except Exception as exc:
        logger.debug(
            "Tesseract OCR unavailable for page",
            extra={"page": page.number, "error": str(exc)},
        )
        return ""


def _ocr_page_llm(page: fitz.Page, settings: Settings) -> str:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
    image_bytes = pixmap.tobytes("jpeg", jpg_quality=85)
    image_b64 = base64.standard_b64encode(image_bytes).decode("ascii")

    payload = {
        "model": settings.pdf_ocr_llm_model,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Извлеки весь видимый текст с изображения документа. "
                            "Сохрани структуру абзацев и заголовков. "
                            "Верни только текст, без комментариев."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                ],
            },
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    if settings.openrouter_http_referer:
        headers["HTTP-Referer"] = settings.openrouter_http_referer
    if settings.openrouter_app_title:
        headers["X-Title"] = settings.openrouter_app_title

    try:
        with httpx.Client(timeout=settings.llm_timeout_sec) as client:
            response = client.post(
                f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
    except Exception as exc:
        logger.warning(
            "LLM OCR failed for page",
            extra={"page": page.number, "error": str(exc)},
        )
        return ""

    choices = body.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [block.get("text", "") for block in content if block.get("type") == "text"]
        return "\n".join(part.strip() for part in parts if part.strip())
    return ""


def _cache_path(file_path: Path) -> Path:
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return file_path.parent / ".pdf-text-cache" / f"{digest}.txt"


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _WHITESPACE_RE.sub("\n", normalized)
    normalized = _MULTI_NEWLINE_RE.sub("\n\n", normalized)
    return normalized.strip()
