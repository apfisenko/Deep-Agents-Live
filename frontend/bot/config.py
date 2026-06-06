"""Bot configuration (fail-fast)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    telegram_bot_token: str = Field(validation_alias="TELEGRAM_BOT_TOKEN")
    backend_url: str = Field(
        default="http://localhost:8000",
        validation_alias="BACKEND_URL",
    )
    telegram_polling_timeout: int = Field(
        default=30,
        validation_alias="TELEGRAM_POLLING_TIMEOUT",
    )
    core_request_timeout_sec: int = Field(default=120, validation_alias="CORE_REQUEST_TIMEOUT_SEC")
    telegram_proxy: str | None = Field(default=None, validation_alias="TELEGRAM_PROXY")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    @property
    def backend_base_url(self) -> str:
        return self.backend_url.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
