"""Кастомные HTTP-роуты companion-сервера: drill-endpoint (A2UI) на :2024.

Agent Server умеет монтировать своё FastAPI-приложение рядом со штатными
роутами — `http.app` в langgraph.json (см. доку «custom routes»). Так канал 2
(формы A2UI; таблица каналов — в README практики) живёт на том же порту,
что и канал 1 (чат): фронту не нужен отдельный сервер под формы. Запасной вариант —
`create_drill_app()` отдельным процессом на :8123 (см. companion/drill/README).

Доставка ответа студента (`CompanionDelivery`) идёт loopback-запросом в этот
же сервер через langgraph_sdk (`COMPANION_URL`, по умолчанию
http://127.0.0.1:2024): drill-endpoint остаётся обычным API-клиентом
companion и ничего не знает про его графы.

Осторожно: кастомные роуты имеют приоритет над штатными — не занимать
пути вроде /threads и /runs (наш /drill/a2ui с ними не пересекается).
"""

from fastapi import FastAPI

from companion.drill import CompanionDelivery, DrillFormGenerator, build_drill_router

app = FastAPI(title="companion custom routes: drill A2UI endpoint")
app.include_router(build_drill_router(DrillFormGenerator(), CompanionDelivery()))
