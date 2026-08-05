"""Pydantic-модели контракта Router."""

from typing import Literal

from pydantic import BaseModel, Field

# "review" намеренно отсутствует — это состояние флоу (пайплайна), не интент пользователя.
RouteDecision = Literal["qa", "homework", "drill", "stay"]


class Intent(BaseModel):
    """Результат классификации интента студента."""

    decision: RouteDecision
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    reasoning: str = Field(default="", description="Краткое обоснование классификации")


class RouterInput(BaseModel):
    """Входные данные для Router."""

    recent_messages: list[str]  # хвост диалога (последние 3 сообщения, только content)
    current_mode: str  # текущий mode из state
