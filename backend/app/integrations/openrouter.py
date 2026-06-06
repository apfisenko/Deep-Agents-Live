"""OpenRouter LLM and embeddings clients."""

import logging
from typing import Any

import httpx
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import APIConnectionError, APIStatusError, APITimeoutError

from app.config import Settings, get_settings
from app.exceptions import AgentCoreError, ModelError, ProviderUnavailableError

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_FALLBACK = "openai/text-embedding-3-small"


def _default_headers(settings: Settings) -> dict[str, str]:
    headers: dict[str, str] = {}
    if settings.openrouter_http_referer:
        headers["HTTP-Referer"] = settings.openrouter_http_referer
    if settings.openrouter_app_title:
        headers["X-Title"] = settings.openrouter_app_title
    return headers


def create_chat_model(settings: Settings | None = None, *, model: str | None = None) -> ChatOpenAI:
    cfg = settings or get_settings()
    return ChatOpenAI(  # type: ignore[call-arg]
        model=model or cfg.llm_model,
        api_key=cfg.openrouter_api_key,
        base_url=cfg.openrouter_base_url,
        temperature=cfg.llm_temperature,
        max_tokens=cfg.llm_max_tokens,
        timeout=cfg.llm_timeout_sec,
        max_retries=0,
        default_headers=_default_headers(cfg),
    )


def create_embeddings(
    settings: Settings | None = None,
    *,
    model: str | None = None,
) -> OpenAIEmbeddings:
    cfg = settings or get_settings()
    return OpenAIEmbeddings(  # type: ignore[call-arg]
        model=model or cfg.embedding_model,
        api_key=cfg.openrouter_api_key,
        base_url=cfg.openrouter_base_url,
        timeout=cfg.embedding_timeout_sec,
        default_headers=_default_headers(cfg),
    )


def _embedding_model_chain(settings: Settings) -> list[str]:
    primary = settings.embedding_model
    fallback = settings.embedding_fallback_model or DEFAULT_EMBEDDING_FALLBACK
    models = [primary]
    if fallback != primary:
        models.append(fallback)
    return models


def embed_documents(texts: list[str], settings: Settings | None = None) -> list[list[float]]:
    cfg = settings or get_settings()
    if not texts:
        return []

    last_error: Exception | None = None
    for model in _embedding_model_chain(cfg):
        embedder = create_embeddings(cfg, model=model)
        try:
            return embedder.embed_documents(texts)
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Embedding model failed",
                extra={"model": model, "error": str(exc)},
            )
    if last_error is None:
        msg = "No embedding models configured"
        raise ModelError(error_code="embedding_model_error", message=msg)
    raise map_openai_exception(last_error) from last_error


def embed_query(text: str, settings: Settings | None = None) -> list[float]:
    cfg = settings or get_settings()
    last_error: Exception | None = None
    for model in _embedding_model_chain(cfg):
        embedder = create_embeddings(cfg, model=model)
        try:
            return embedder.embed_query(text)
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Embedding model failed",
                extra={"model": model, "error": str(exc)},
            )
    if last_error is None:
        msg = "No embedding models configured"
        raise ModelError(error_code="embedding_model_error", message=msg)
    raise map_openai_exception(last_error) from last_error


def map_openai_exception(exc: Exception) -> AgentCoreError:
    if isinstance(exc, ValueError) and "embedding" in str(exc).lower():
        return ModelError(
            message=(
                "Модель embeddings не вернула данные. "
                "Используйте openai/text-embedding-3-small через OpenRouter."
            ),
            error_code="embedding_model_error",
        )
    if isinstance(exc, APITimeoutError):
        return ProviderUnavailableError(error_code="openrouter_timeout")
    if isinstance(exc, APIConnectionError):
        return ProviderUnavailableError(error_code="openrouter_connection_error")
    if isinstance(exc, APIStatusError):
        status = exc.status_code
        if status in {502, 503, 504}:
            return ProviderUnavailableError(error_code=f"openrouter_{status}")
        if status in {400, 404, 429}:
            return ModelError(error_code="model_unavailable")
        return ProviderUnavailableError(error_code="openrouter_502")
    if isinstance(exc, httpx.TimeoutException):
        return ProviderUnavailableError(error_code="openrouter_timeout")
    if isinstance(exc, httpx.ConnectError):
        return ProviderUnavailableError(error_code="openrouter_connection_error")
    logger.exception("Unhandled LLM error", exc_info=exc)
    return ModelError(error_code="model_error")


def invoke_with_fallback(
    operation: str,
    primary_model: str,
    fallback_model: str,
    runner: Any,
) -> Any:
    """Run LLM operation with optional single fallback on model errors."""
    settings = get_settings()
    try:
        return runner(create_chat_model(settings, model=primary_model))
    except (APIStatusError, APITimeoutError, APIConnectionError, httpx.HTTPError) as exc:
        mapped = map_openai_exception(exc)
        if (
            isinstance(mapped, ModelError)
            and fallback_model
            and fallback_model != primary_model
        ):
            logger.warning(
                "LLM fallback",
                extra={"operation": operation, "from": primary_model, "to": fallback_model},
            )
            try:
                return runner(create_chat_model(settings, model=fallback_model))
            except (
                APIStatusError,
                APITimeoutError,
                APIConnectionError,
                httpx.HTTPError,
            ) as fallback_exc:
                raise map_openai_exception(fallback_exc) from fallback_exc
        raise mapped from exc
