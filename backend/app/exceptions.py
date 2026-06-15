"""Application-specific exceptions."""

from typing import Any


class AgentCoreError(Exception):
    """Base error for Agent Core."""

    def __init__(
        self,
        message: str,
        *,
        error_class: str,
        error_code: str,
        retryable: bool,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_class = error_class
        self.error_code = error_code
        self.retryable = retryable

    def to_detail(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "error_class": self.error_class,
            "error_code": self.error_code,
            "retryable": self.retryable,
        }


class ProviderUnavailableError(AgentCoreError):
    def __init__(self, message: str = "Сервис ИИ временно недоступен", *, error_code: str) -> None:
        super().__init__(
            message,
            error_class="provider_unavailable",
            error_code=error_code,
            retryable=True,
        )


class ModelError(AgentCoreError):
    def __init__(
        self,
        message: str = "Не удалось обработать запрос (модель)",
        *,
        error_code: str = "model_error",
    ) -> None:
        super().__init__(
            message,
            error_class="model_error",
            error_code=error_code,
            retryable=False,
        )


class ConfigNotFoundError(AgentCoreError):
    def __init__(self, message: str, *, config_id: str) -> None:
        super().__init__(
            message,
            error_class="config_error",
            error_code="config_not_found",
            retryable=False,
        )
        self.config_id = config_id
