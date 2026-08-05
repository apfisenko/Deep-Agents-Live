"""Кейс дрилла — контракт входа модуля."""

from __future__ import annotations

from pydantic import BaseModel, Field

SUBMIT_EVENT = "submit_drill_answer"
RATIONALE_KEY = "rationale"

_SLUG = r"^[A-Za-z0-9][A-Za-z0-9_-]*$"


class AxisOption(BaseModel):
    """Один вариант выбора на оси."""

    value: str
    label: str


class CaseAxis(BaseModel):
    """Ось кейса: один вопрос с выбором варианта."""

    id: str = Field(pattern=_SLUG)
    question: str
    options: list[AxisOption] = Field(min_length=2)


class DrillCase(BaseModel):
    """Кейс дрилла: сценарий + выборы по осям + свободное обоснование."""

    case_id: str = Field(pattern=_SLUG)
    title: str
    scenario: str
    axes: list[CaseAxis] = Field(min_length=1)
    free_question: str = "Обоснуй выбор: какие факты кейса его определили?"

    @property
    def surface_id(self) -> str:
        return f"drill-{self.case_id}"
