"""Router — классификационный узел перед companion (паттерн Router).

Одно грубое решение на каждое сообщение студента: какой режим его обслуживает.
Никого не вызывает и не ведёт диалог — только штампует `mode` в state
(вариант «classify → configure»; канонический «classify → dispatch» — см.
examples/router_canonical.py).

Sticky: видит текущий режим и хвост диалога, умеет ответить «stay» — чтобы
«да, подтверждаю» посреди сдачи не улетело в qa, а «объясни пункт 2» не
выбило из review.
"""

from __future__ import annotations

import logging
from typing import Literal

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from pydantic import BaseModel, Field

from companion.modes import DEFAULT_MODE

logger = logging.getLogger("companion.router")

# Служебные сообщения (поллер проверок и drill-доставка) режим НЕ меняют:
# это не интент студента, а транспорт результата — классификатору их не даём
# (иначе «проверка завершена — забери результат» может выбить из drill
# посреди заполнения формы).
SERVICE_PREFIXES = ("[авто]", "[drill]")

ROUTER_SYSTEM = """\
Ты — маршрутизатор ассистента студента. По новому сообщению студента и \
контексту диалога выбери ровно одно:
- "qa" — вопрос о курсе (программа, темы, формат, организация, домашки «как устроено»),
  смена темы на вопросы о курсе;
- "homework" — студент хочет СДАТЬ домашку на проверку (даёт/собирается дать
  репозиторий или путь к коду и тему);
- "drill" — студент хочет ПОТРЕНИРОВАТЬСЯ: просит кейс/задачу/тренажёр
  («хочу потренироваться», «дай кейс», «потренируй меня», «дрилл»);
- "stay" — сообщение продолжает текущее дело в текущем режиме: подтверждение,
  ответ на вопрос ассистента, недостающие данные сдачи, просьбы объяснить/разобрать
  уже полученный фидбек, уточнения по нему, обсуждение текущего кейса тренажёра.

Правила:
- Сомневаешься между stay и сменой — выбирай stay.
- Просьбы «объясни пункт фидбека», «как исправить замечание» после проверки — stay.
- Реплики про текущий кейс тренажёра («ещё кейс», «а почему так») в режиме drill — stay.
- Явный новый вопрос о курсе после завершённого дела — qa.
"""


class RouteDecision(BaseModel):
    """Structured output классификатора."""

    decision: Literal["qa", "homework", "drill", "stay"] = Field(
        description="Режим для нового сообщения студента (stay = не менять)"
    )


def _render_tail(messages: list[AnyMessage], limit: int = 6) -> str:
    """Хвост диалога для контекста классификации (только Human/AI, кратко)."""
    lines: list[str] = []
    for msg in messages[-limit * 2 :]:
        if isinstance(msg, HumanMessage):
            role = "студент"
        elif isinstance(msg, AIMessage) and not msg.tool_calls:
            role = "ассистент"
        else:
            continue
        text = msg.content if isinstance(msg.content, str) else str(msg.content)
        lines.append(f"{role}: {text[:200]}")
    return "\n".join(lines[-limit:]) if lines else "(начало диалога)"


def build_router_node(model):
    """Узел внешнего графа: классифицировал → обновил mode (и только его)."""
    # nostream: служебный LLM-вызов классификатора не должен утекать клиентам
    # в stream_mode="messages" (веб-чат видел бы сырой {"decision": ...}).
    structured = model.with_structured_output(RouteDecision).with_config(
        {"tags": ["nostream"]}
    )

    def route(state: dict) -> dict:
        mode = state.get("mode") or DEFAULT_MODE
        messages: list[AnyMessage] = state.get("messages", [])
        tail = _render_tail(messages[:-1])
        new_text = ""
        if messages and isinstance(messages[-1], HumanMessage):
            last = messages[-1]
            new_text = last.content if isinstance(last.content, str) else str(last.content)
        if new_text.startswith(SERVICE_PREFIXES):
            logger.info("router: служебное сообщение — остаёмся в %s", mode)
            return {"mode": mode}
        prompt = (
            f"Текущий режим: {mode}\n\nХвост диалога:\n{tail}\n\n"
            f"Новое сообщение студента: {new_text}"
        )
        try:
            decision: RouteDecision = structured.invoke(
                [("system", ROUTER_SYSTEM), ("user", prompt)]
            )
            choice = decision.decision
        except Exception:  # noqa: BLE001 — сбой классификатора не валит диалог
            logger.warning("router: сбой классификации, остаёмся в %s", mode)
            choice = "stay"
        new_mode = mode if choice == "stay" else choice
        logger.info("router: %s → %s (decision=%s)", mode, new_mode, choice)
        return {"mode": new_mode}

    return route
