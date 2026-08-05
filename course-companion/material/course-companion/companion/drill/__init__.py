"""Drill-режим: генерация A2UI-форм кейса тренажёра (ступень 4).

Модуль изолирован от остального companion:
- `case`      — контракт входа: кейс дрилла (его пишет companion в стейт);
- `generator` — форма кейса = ОДИН отдельный LLM-вызов со схемным промптом A2UI;
- `delivery`  — доставка userAction (ответа студента) в тред companion через SDK;
- `routes`    — HTTP-шов для фронта: POST + SSE.
"""

from companion.drill.case import AxisOption, CaseAxis, DrillCase
from companion.drill.delivery import CompanionDelivery, format_action_message
from companion.drill.generator import DrillFormGenerator, FormGenerationError
from companion.drill.routes import build_drill_router, create_drill_app

__all__ = [
    "AxisOption",
    "CaseAxis",
    "CompanionDelivery",
    "DrillCase",
    "DrillFormGenerator",
    "FormGenerationError",
    "build_drill_router",
    "create_drill_app",
    "format_action_message",
]
