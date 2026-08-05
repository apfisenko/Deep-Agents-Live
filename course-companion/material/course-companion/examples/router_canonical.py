"""Канонический Router-паттерн: «classify → dispatch».

Контраст с основной системой практики: здесь шаг классификации отправляет
запрос НАПРЯМУЮ в специализированного агента (`Command(goto=...)`), и тот
сам формирует финальный ответ — верхнего диалогового агента нет вообще.
Такой router хорош для one-shot запросов, чётких вертикалей и параллельного
fan-out; цена — нет единого многоходового диалога со студентом. Основная
система практики вместо этого ставит режим (mode) единственному говорящему
агенту («classify → configure») — сравни с companion/router.py и modes.py.

Запуск: uv run python examples/router_canonical.py
"""

from pathlib import Path
from typing import Literal

from langchain.agents import create_agent
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field

from companion.config import build_model
from companion.subagents.course_qa import build_kb_tools

KB_DIR = Path(__file__).resolve().parents[1] / "data" / "kb"

model = build_model()

# --- Специализированные агенты-вертикали: каждый отвечает пользователю САМ ---
qa_agent = create_agent(
    model=model,
    tools=build_kb_tools(KB_DIR),
    system_prompt=(
        "Ты — консультант по базе знаний курса. Сначала посмотри оглавление "
        "(list_kb_docs), прочитай только релевантные документы и ответь кратко, "
        "по-русски, строго по их содержимому."
    ),
)
smalltalk_agent = create_agent(
    model=model,
    tools=[],
    system_prompt=(
        "Ты — дружелюбный ассистент курса. Поддержи короткий разговор "
        "(приветствия, благодарности, болтовня) и мягко предложи задать "
        "вопрос по курсу. Отвечай по-русски, одним-двумя предложениями."
    ),
)


class Route(BaseModel):
    """Structured output классификатора: только выбор маршрута, ничего больше."""

    route: Literal["qa", "smalltalk"] = Field(
        description="qa — вопрос по курсу/программе/домашкам; smalltalk — всё остальное"
    )


def router(state: MessagesState) -> Command[Literal["qa_agent", "smalltalk_agent"]]:
    """Разовый шаг классификации: решает, КУДА отправить запрос, и не ведёт диалог."""
    question = state["messages"][-1].content
    decision = model.with_structured_output(Route).invoke(
        f"Классифицируй запрос студента курса.\n\nЗапрос: {question}"
    )
    target = "qa_agent" if decision.route == "qa" else "smalltalk_agent"
    print(f"[router] «{question}» → {target}")
    return Command(goto=target)


builder = StateGraph(MessagesState)
builder.add_node("router", router)
builder.add_node("qa_agent", qa_agent)  # compiled-агент вставлен узлом как есть
builder.add_node("smalltalk_agent", smalltalk_agent)
builder.add_edge(START, "router")
builder.add_edge("qa_agent", END)
builder.add_edge("smalltalk_agent", END)
graph = builder.compile()

# Параллельный fan-out: если запрос покрывает несколько вертикалей сразу,
# router вместо одного goto возвращает список Send — каждый агент получает
# свою часть запроса, а отдельный узел-синтезатор собирает ответы воедино:
#     from langgraph.types import Send
#     return [Send("qa_agent", {"messages": [...]}), Send("billing_agent", {...})]

if __name__ == "__main__":
    result = graph.invoke({"messages": [("user", "Что будет в теме 12?")]})
    print(f"\n[ответ] {result['messages'][-1].content}")
