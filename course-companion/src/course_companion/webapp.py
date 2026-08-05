"""Кастомные HTTP-роуты companion-сервера (http.app в langgraph.companion.json)."""

from fastapi import FastAPI

from course_companion.drill import CompanionDelivery, DrillFormGenerator, build_drill_router

app = FastAPI(title="companion custom routes: drill A2UI endpoint")
app.include_router(build_drill_router(DrillFormGenerator(), CompanionDelivery()))
