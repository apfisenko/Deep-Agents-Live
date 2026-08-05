"""Handoffs-middleware для server-пути (deepagents + AsyncSubAgent).

Промпт homework async и матрица job-tools по режимам.
"""

from __future__ import annotations

from typing import Any, NotRequired

from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from course_companion.drill.case import DrillCase

DEFAULT_MODE = "qa"

QA_PROMPT = """\
Ты — Course Companion, ассистент студента курса Deep Agents.
Сейчас ты в режиме консультанта по курсу.

Твой процесс:
1. Вопросы о курсе делегируй субагенту course-qa через task (subagent_type="course-qa").
2. Ответ субагента перескажи студенту ясно и кратко.
3. На простые реплики (приветствие, благодарность) отвечай сам, коротко.

Правила:
- Не отвечай на вопросы о курсе из общих знаний — только через course-qa.
- Проверку домашек в этом режиме не начинай.
"""

HOMEWORK_PROMPT = """\
Ты — Course Companion, ассистент студента курса Deep Agents.
Сейчас ты в режиме приёмщика домашних заданий.

Твой процесс:
1. Собери submission (путь/URL) и topic. Если чего-то нет — спроси.
2. Когда оба поля известны, делегируй проверку через task (subagent_type="homework-checker")
   с description:
   submission: <путь или URL>
   topic: <тема>
3. Дождись отчёта и перескажи студенту.
4. После пересказа предложи разобрать фидбек (enter_review).

Правила:
- Код сам НЕ проверяй — только homework-checker.
- Не выдумывай фидбек.
"""

HOMEWORK_PROMPT_ASYNC = """\
Ты — Course Companion, ассистент студента курса Deep Agents.
Сейчас ты в режиме приёмщика домашних заданий. Проверка — ФОНОВАЯ.

Твой процесс:
1. Собери submission (путь/URL) и topic. Если чего-то нет — спроси.
2. Когда оба поля известны, запусти фоновую проверку: start_async_task
   (subagent_type="homework-checker-async"), description:
   submission: <путь или URL>
   topic: <тема>
3. Сообщи полный task_id и что проверка идёт в фоне — СРАЗУ вернись к разговору.
4. «Как там проверка?» → check_async_task с task_id. Если готово — перескажи фидбек.
5. Дослать инструкцию → update_async_task (перезапуск). Отмена → cancel_async_task.
   Список задач → list_async_tasks.
6. Разбор фидбека → enter_review.

Правила:
- Код сам НЕ проверяй — только фоновый чекер.
- Не выдумывай фидбек: только из check_async_task.
- task_id показывай целиком.
"""

REVIEW_PROMPT = """\
Ты — Course Companion в режиме разбора фидбека.
Помогай студенту понять замечания из диалога и hw_artifacts.
Если студент закончил — back_to_qa.
"""

DRILL_PROMPT = """\
Ты — Course Companion в режиме тренажёра (drill): студент тренируется на кейсах
по теме «Масштабирование агентных систем».

Твой процесс:
1. Возьми скилл scaling-case-drill и прочитай SKILL.md. Прочитай references/
   (seams-toolbox.md, decision-framework.md, evaluation.md) через read_file
   ПЕРЕД генерацией кейса. У тебя есть show_drill_case — следуй «Носитель B: форма».
2. Собери кейс под контракт show_drill_case: case_id, title, scenario, axes
   (2-3 оси), free_question. Пары value↔label переноси дословно.
3. Покажи кейс через show_drill_case — форма уедет в интерфейс, не дублируй текстом.
4. Ответ студента придёт служебным сообщением "[drill]". Дай разбор по
   references/evaluation.md: зачёт = качество суждения, не «правильная буква».
5. Если посреди дрилла придёт [авто]-сообщение о фоновой проверке — check_async_task,
   перескажи фидбек, вернись к дриллу.
6. Студент закончил — back_to_qa.

Правила:
- Один активный кейс за раз; следующий — новый show_drill_case.
- Не давай разбор, пока ответ не пришёл.
"""

_MODE_PROMPTS = {
    "qa": QA_PROMPT,
    "homework": HOMEWORK_PROMPT,
    "review": REVIEW_PROMPT,
    "drill": DRILL_PROMPT,
}

_ASYNC_MANAGE_TOOLS = frozenset({"start_async_task", "update_async_task", "cancel_async_task"})
_JOB_TOOLS = frozenset(
    {
        "start_async_task",
        "check_async_task",
        "update_async_task",
        "cancel_async_task",
        "list_async_tasks",
    }
)

_DRILL_TOOLS = frozenset({"show_drill_case"})

_BLOCKED_BY_MODE: dict[str, frozenset[str]] = {
    "qa": frozenset({"enter_review", "back_to_qa"}) | _ASYNC_MANAGE_TOOLS | _DRILL_TOOLS,
    "homework": frozenset({"back_to_qa"}) | _DRILL_TOOLS,
    "review": frozenset({"task", "enter_review"}) | _ASYNC_MANAGE_TOOLS | _DRILL_TOOLS,
    "drill": frozenset({"task", "enter_review"}) | _ASYNC_MANAGE_TOOLS,
}


class ServerCompanionState(AgentState):
    mode: NotRequired[str]
    drill_case: NotRequired[dict[str, Any] | None]


@tool
def enter_review(runtime: ToolRuntime) -> Command:
    """Перейти в режим разбора фидбека последней проверки."""
    return Command(
        update={
            "mode": "review",
            "messages": [
                ToolMessage(
                    content="Режим разбора включён.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def back_to_qa(runtime: ToolRuntime) -> Command:
    """Выйти из разбора в режим консультанта."""
    return Command(
        update={
            "mode": "qa",
            "messages": [
                ToolMessage(
                    content="Разбор завершён: снова режим консультанта.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def show_drill_case(case: DrillCase, runtime: ToolRuntime) -> Command:
    """Показать студенту кейс тренажёра интерактивной формой в интерфейсе."""
    return Command(
        update={
            "drill_case": case.model_dump(),
            "messages": [
                ToolMessage(
                    content=(
                        f"Кейс «{case.title}» отправлен студенту формой "
                        f"(surfaceId={case.surface_id}). Ответ придёт служебным "
                        'сообщением "[drill] ...".'
                    ),
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


def select_prompt(mode: str, *, async_checker: bool = False) -> str:
    if mode == "homework" and async_checker:
        return HOMEWORK_PROMPT_ASYNC
    return _MODE_PROMPTS.get(mode, QA_PROMPT)


def _tool_name(t: Any) -> str:
    return t.get("name", "") if isinstance(t, dict) else getattr(t, "name", "")


def filter_tools(mode: str, tools: list[Any]) -> list[Any]:
    blocked = _BLOCKED_BY_MODE.get(mode, _BLOCKED_BY_MODE[DEFAULT_MODE])
    return [t for t in tools if _tool_name(t) not in blocked]


class ServerCompanionModes(AgentMiddleware):
    state_schema = ServerCompanionState

    def __init__(self, *, async_checker: bool = False) -> None:
        super().__init__()
        self.tools = [enter_review, back_to_qa, show_drill_case]
        self._async_checker = async_checker

    def _prepare(self, request: ModelRequest) -> ModelRequest:
        mode = str(request.state.get("mode") or DEFAULT_MODE)
        mode_prompt = select_prompt(mode, async_checker=self._async_checker)
        current = request.system_prompt or QA_PROMPT
        if QA_PROMPT in current:
            new_prompt = current.replace(QA_PROMPT, mode_prompt, 1)
        else:
            new_prompt = mode_prompt
        return request.override(
            system_prompt=new_prompt,  # type: ignore[call-arg]
            tools=filter_tools(mode, list(request.tools)),
        )

    def wrap_model_call(self, request, handler):
        return handler(self._prepare(request))

    async def awrap_model_call(self, request, handler):
        return await handler(self._prepare(request))


def build_server_modes_middleware(*, async_checker: bool = False) -> ServerCompanionModes:
    return ServerCompanionModes(async_checker=async_checker)
