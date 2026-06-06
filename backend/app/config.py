"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.paths import DEFAULT_LEADS_PATH, REPO_ROOT


class Settings(BaseSettings):
    """Runtime settings with fail-fast validation on startup."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    env: str = Field(validation_alias="ENV")

    backend_host: str = Field(default="0.0.0.0", validation_alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, validation_alias="BACKEND_PORT")
    cors_origins: str = Field(
        default="http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )

    openrouter_api_key: str = Field(validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias="OPENROUTER_BASE_URL",
    )
    llm_model: str = Field(default="openai/gpt-4o-mini", validation_alias="LLM_MODEL")
    llm_fallback_model: str = Field(default="", validation_alias="LLM_FALLBACK_MODEL")
    embedding_model: str = Field(
        default="openai/text-embedding-3-small",
        validation_alias="EMBEDDING_MODEL",
    )
    embedding_fallback_model: str = Field(
        default="openai/text-embedding-3-small",
        validation_alias="EMBEDDING_FALLBACK_MODEL",
    )
    llm_timeout_sec: int = Field(default=60, validation_alias="LLM_TIMEOUT_SEC")
    embedding_timeout_sec: int = Field(default=30, validation_alias="EMBEDDING_TIMEOUT_SEC")
    llm_max_tokens: int = Field(default=2048, validation_alias="LLM_MAX_TOKENS")
    llm_temperature: float = Field(default=0.2, validation_alias="LLM_TEMPERATURE")
    openrouter_http_referer: str = Field(default="", validation_alias="OPENROUTER_HTTP_REFERER")
    openrouter_app_title: str = Field(
        default="Deep-Agents-Live",
        validation_alias="OPENROUTER_APP_TITLE",
    )

    langfuse_enabled: bool = Field(default=False, validation_alias="LANGFUSE_ENABLED")
    langfuse_public_key: str = Field(default="", validation_alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", validation_alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(
        default="http://localhost:3001",
        validation_alias="LANGFUSE_HOST",
    )
    langfuse_request_timeout_sec: int = Field(
        default=5,
        validation_alias="LANGFUSE_REQUEST_TIMEOUT_SEC",
    )

    mock_payment_base_url: str = Field(
        default="https://pay.mock.llmstart.ru",
        validation_alias="MOCK_PAYMENT_BASE_URL",
    )
    mock_payment_confirm_keywords: str = Field(
        default="оплатил,оплатила,оплачено",
        validation_alias="MOCK_PAYMENT_CONFIRM_KEYWORDS",
    )
    leads_file_path: str = Field(
        default=str(DEFAULT_LEADS_PATH),
        validation_alias="LEADS_FILE_PATH",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def confirm_keywords_list(self) -> list[str]:
        return [
            keyword.strip().lower()
            for keyword in self.mock_payment_confirm_keywords.split(",")
            if keyword.strip()
        ]

    @property
    def leads_path(self) -> str:
        path = self.leads_file_path
        if not path.startswith("/") and ":" not in path[:3]:
            return str((REPO_ROOT / path).resolve())
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
