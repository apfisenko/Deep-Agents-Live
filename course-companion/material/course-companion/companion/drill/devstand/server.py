"""Dev-only стенд drill-модуля: drill-endpoint + тестовый кейс-заглушка.

НЕ часть продукта: живой прогон модуля без companion-сервера (фаза 2C).
Отличия от боевой сборки (фаза 3):
- кейс не приходит из стейта companion, а захардкожен здесь (GET /devstand/case);
- доставка userAction идёт не в живой тред, а в LoggingStubClient — он
  записывает, что drill-модуль ПОПЫТАЛСЯ создать run (GET /devstand/delivered).

Запуск:  uv run python server.py     (drill-endpoint на :8123)
Клиент:  client/ (vite, :5273) — см. README модуля.

DRILL_FAIL_FIRST=1 — демо retry-пути: первая LLM-попытка подменяется заведомо
неполной формой (без кнопки) -> генератор бракует её, убирает частичную
поверхность deleteSurface'ом и повторяет попытку уже живой LLM.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Стенд живёт внутри пакета companion, но запускается как скрипт —
# добавляем корень course-companion, чтобы импортировался companion.drill.
COURSE_COMPANION_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(COURSE_COMPANION_ROOT))
load_dotenv(COURSE_COMPANION_ROOT / ".env")  # OPENAI_API_KEY / _BASE_URL / _MODEL

from companion.drill import (  # noqa: E402
    AxisOption,
    CaseAxis,
    CompanionDelivery,
    DrillCase,
    DrillFormGenerator,
    create_drill_app,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("drill.devstand")

# --- Кейс-заглушка (SKILL.md тренажёра ещё нет — тема из дизайна Т12:
# --- «какой протокол на каком шве») --------------------------------------------
STUB_CASE = DrillCase(
    case_id="protocol-seams-01",
    title="Кейс: выбор протокола на шов",
    scenario=(
        "Вы делаете саппорт-ассистента FinPeak: агент отвечает клиентам в веб-виджете. "
        "Два новых требования. (1) Долгие проверки транзакций надо отдавать агенту-аналитику "
        "биллинга — его делает ДРУГАЯ команда на другом фреймворке и обещает только "
        "«стандартный внешний интерфейс»; проверка идёт минуты, чат не должен виснуть. "
        "(2) Продукт хочет динамические анкеты в виджете: состав полей зависит от кейса "
        "клиента и известен только в рантайме."
    ),
    axes=[
        CaseAxis(
            id="billing_seam",
            question="Каким протоколом связать ассистента с агентом биллинга?",
            options=[
                AxisOption(value="agent_protocol", label="Agent Protocol — штатный шов нашего стека"),
                AxisOption(value="a2a", label="A2A — межвендорный стандарт agent-to-agent"),
                AxisOption(value="mcp", label="MCP — подключить чужого агента как tool-сервер"),
                AxisOption(value="custom_rest", label="Свой REST API и поллинг руками"),
            ],
        ),
        CaseAxis(
            id="ui_channel",
            question="Как доставлять динамические анкеты в виджет?",
            options=[
                AxisOption(value="a2ui", label="A2UI — агент декларативно описывает UI"),
                AxisOption(value="ag_ui", label="AG-UI — событийный протокол agent-user interaction"),
                AxisOption(value="state_stream", label="Стриминг стейта + свои React-компоненты"),
                AxisOption(value="hardcoded", label="Захардкодить все варианты анкет во фронте"),
            ],
        ),
    ],
    free_question="Обоснуй оба выбора: какие факты кейса их определили и чем ты за это платишь?",
)


# --- Заглушка доставки: тот же интерфейс, что у langgraph_sdk-клиента ------------
class _StubRuns:
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records

    async def create(self, thread_id: str, assistant_id: str, **kwargs: Any) -> dict[str, Any]:
        record = {
            "thread_id": thread_id,
            "assistant_id": assistant_id,
            "input": kwargs.get("input"),
            "multitask_strategy": kwargs.get("multitask_strategy"),
        }
        self._records.append(record)
        log.info("STUB delivery: runs.create -> %s", record)
        return {"run_id": f"stub-run-{len(self._records)}", "status": "pending"}


class LoggingStubClient:
    """Мимикрия под LangGraphClient: только runs.create, всё пишется в память."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self.runs = _StubRuns(self.records)


# --- Демо retry (DRILL_FAIL_FIRST=1): первая попытка — неполная форма ------------
def _broken_first_attempt(case: DrillCase) -> str:
    """Правдоподобный «обрыв LLM»: поверхность и заголовок есть, кнопки нет."""
    import json

    from companion.drill.generator import CATALOG_ID, SPEC_VERSION

    messages = [
        {
            "version": SPEC_VERSION,
            "createSurface": {"surfaceId": case.surface_id, "catalogId": CATALOG_ID},
        },
        {
            "version": SPEC_VERSION,
            "updateComponents": {
                "surfaceId": case.surface_id,
                "components": [
                    {"id": "root", "component": "Card", "child": "title"},
                    {"id": "title", "component": "Text", "variant": "h3", "text": case.title},
                ],
            },
        },
    ]
    return f"<a2ui-json>{json.dumps(messages, ensure_ascii=False)}</a2ui-json>"


def _make_generator() -> DrillFormGenerator:
    gen = DrillFormGenerator()
    if os.environ.get("DRILL_FAIL_FIRST") != "1":
        return gen
    live = gen._tokens  # noqa: SLF001 — dev-only подмена стрима ради демо retry
    state = {"first": True}

    async def flaky(case: DrillCase):
        if state["first"]:
            state["first"] = False
            log.warning("DRILL_FAIL_FIRST: ломаю первую попытку (демо retry)")
            yield _broken_first_attempt(case)
            return
        async for token in live(case):
            yield token

    gen._tokens = flaky  # noqa: SLF001
    return gen


stub_client = LoggingStubClient()
app = create_drill_app(
    generator=_make_generator(),
    delivery=CompanionDelivery(client=stub_client),
)


@app.get("/devstand/case")
async def devstand_case() -> dict[str, Any]:
    """Кейс-заглушка для клиента стенда (в фазе 3 кейс придёт из стейта companion)."""
    return STUB_CASE.model_dump()


@app.get("/devstand/delivered")
async def devstand_delivered() -> list[dict[str, Any]]:
    """Что drill-модуль доставил бы в тред companion (лог заглушки)."""
    return stub_client.records


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8123)
