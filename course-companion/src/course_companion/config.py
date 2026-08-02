"""Runtime configuration — загружается из окружения, падает сразу при отсутствии ключей."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация приложения.

    Загружает переменные из `.env` и проверяет наличие обязательных ключей.
    Падает с `ValueError` на старте процесса, не в момент первого использования.
    """

    def __init__(self) -> None:
        self.openrouter_api_key: str = self._require("OPENROUTER_API_KEY")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.reviews_dir: str = os.getenv("REVIEWS_DIR", "./reviews")

    @staticmethod
    def _require(name: str) -> str:
        value = os.getenv(name)
        if not value:
            msg = (
                f"Обязательная переменная окружения '{name}' не задана. "
                f"Создайте файл .env на основе .env.example."
            )
            raise ValueError(msg)
        return value
