"""Внешний custom workflow: router → companion.

Паттерн Custom workflow вживую: детерминированно расположенный
классификационный шаг (LLM внутри, позиция в графе жёсткая) + целый
deepagents-агент, вставленный узлом-подграфом. Общий типизированный state:
`messages` + `mode` — каналы совпадают по именам со схемой companion
(поле mode приносит CompanionModes-middleware), поэтому компилированный
агент добавляется в add_node напрямую, без обёртки.

Два режима сборки:
- CLI (по умолчанию): checkpointer InMemorySaver — многоходовость живёт
  в памяти процесса, thread_id = сессия чата.
- Agent Server (`server=True`): граф компилируется БЕЗ чекпоинтера —
  персистентность (threads/checkpoints) отдаёт платформа, локальный
  checkpointer она бы всё равно проигнорировала.
"""

from __future__ import annotations

from typing import Annotated, Any, NotRequired, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from companion.agent import build_companion
from companion.config import build_model
from companion.router import build_router_node


def _merge_async_tasks(
    existing: dict[str, Any] | None, update: dict[str, Any]
) -> dict[str, Any]:
    """Тот же merge-редьюсер, что у канала async_tasks внутри deepagents."""
    merged = dict(existing or {})
    merged.update(update)
    return merged


class CompanionGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    mode: NotRequired[str]
    # Канал фоновых задач: живёт внутри companion-подграфа (AsyncSubAgent-
    # middleware deepagents), но объявлен и здесь — совпадающие по имени каналы
    # подграф отдаёт наружу, и клиенты сервера видят задачи в values треда
    # (на этом стоит фронт-поллер «результат пришёл сам»).
    async_tasks: Annotated[NotRequired[dict[str, Any]], _merge_async_tasks]
    # Кейс тренажёра (drill-режим): show_drill_case пишет его в стейт companion,
    # тот же принцип «совпадающий канал подграф отдаёт наружу» — фронт видит
    # кейс в values и монтирует A2UI-surface (§1.2 дизайна практики).
    drill_case: NotRequired[dict[str, Any] | None]


def build_graph(checkpointer=None, *, server: bool = False):
    """Собрать внешний граф.

    По умолчанию (CLI) — InMemorySaver + синхронный чекер. `server=True` —
    без чекпоинтера (его подставляет Agent Server) и с фоновым чекером
    (AsyncSubAgent на граф "checker"); см. развилку в build_companion.
    """
    model = build_model()
    router = build_router_node(build_model(max_tokens=256, temperature=0.0))
    companion = build_companion(model=model, async_checker=server)

    graph = StateGraph(CompanionGraphState)
    graph.add_node("router", router)
    graph.add_node("companion", companion)
    graph.add_edge(START, "router")
    graph.add_edge("router", "companion")
    graph.add_edge("companion", END)
    if server:
        return graph.compile()
    return graph.compile(checkpointer=checkpointer or InMemorySaver())
