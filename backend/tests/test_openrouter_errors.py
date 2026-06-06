"""OpenRouter error mapping tests."""

import httpx
from app.exceptions import ModelError, ProviderUnavailableError
from app.integrations.openrouter import map_openai_exception
from openai import APIConnectionError, APITimeoutError


def test_map_timeout_to_provider_unavailable() -> None:
    mapped = map_openai_exception(APITimeoutError(request=None))
    assert isinstance(mapped, ProviderUnavailableError)
    assert mapped.error_code == "openrouter_timeout"


def test_map_connection_error() -> None:
    mapped = map_openai_exception(APIConnectionError(request=None))
    assert isinstance(mapped, ProviderUnavailableError)
    assert mapped.error_code == "openrouter_connection_error"


def test_map_connect_error() -> None:
    mapped = map_openai_exception(httpx.ConnectError("down"))
    assert isinstance(mapped, ProviderUnavailableError)


def test_map_empty_embedding_response() -> None:
    mapped = map_openai_exception(ValueError("No embedding data received"))
    assert isinstance(mapped, ModelError)
    assert mapped.error_code == "embedding_model_error"


def test_detail_payload_shape() -> None:
    mapped = ModelError(error_code="model_unavailable")
    detail = mapped.to_detail()
    assert detail["error_class"] == "model_error"
    assert detail["retryable"] is False
