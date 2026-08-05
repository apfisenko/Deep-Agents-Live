"""Кейс дрилла — контракт входа модуля.

Это единственное, что drill-модуль хочет знать о тренажёре: текст сценария,
оси выбора с вариантами и свободный вопрос-обоснование. В фазе 3 companion
(SKILL.md-логика drill-режима) кладёт такую структуру в свой стейт, фронт
видит её через useStream и POST-ит на drill-endpoint как JSON.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# Имя события кнопки «Отправить» — по нему сервер узнаёт ответ студента.
SUBMIT_EVENT = "submit_drill_answer"
# Ключ свободного ответа в data model формы (оси занимают свои id).
RATIONALE_KEY = "rationale"


class AxisOption(BaseModel):
    """Один вариант выбора на оси."""

    value: str  # машинное значение (уедет в userAction.context)
    label: str  # что видит студент


# id осей и кейса становятся путями data model и surfaceId — держим их
# машинными (латиница/цифры/дефис/подчёркивание), схема это проверяет.
_SLUG = r"^[A-Za-z0-9][A-Za-z0-9_-]*$"


class CaseAxis(BaseModel):
    """Ось кейса: один вопрос с выбором варианта."""

    id: str = Field(pattern=_SLUG)  # станет путём /<id> в data model формы
    question: str
    options: list[AxisOption] = Field(min_length=2)


class DrillCase(BaseModel):
    """Кейс дрилла: сценарий + выборы по осям + свободное обоснование."""

    case_id: str = Field(pattern=_SLUG)  # попадёт в surfaceId формы
    title: str
    scenario: str  # текст кейса, показывается в самой форме
    axes: list[CaseAxis] = Field(min_length=1)
    free_question: str = "Обоснуй выбор: какие факты кейса его определили?"

    @property
    def surface_id(self) -> str:
        """surfaceId формы. Несёт case_id: по нему userAction соотносится с кейсом."""
        return f"drill-{self.case_id}"
