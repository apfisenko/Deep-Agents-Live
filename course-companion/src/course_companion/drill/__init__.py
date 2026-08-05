"""Drill-режим: генерация A2UI-форм кейса тренажёра."""

from course_companion.drill.case import AxisOption, CaseAxis, DrillCase
from course_companion.drill.delivery import CompanionDelivery, format_action_message
from course_companion.drill.generator import DrillFormGenerator, FormGenerationError
from course_companion.drill.routes import build_drill_router, create_drill_app

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
