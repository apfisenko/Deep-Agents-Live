"""Handoffs-машина Course Companion: четыре состояния одного говорящего агента.

Mode — состояние конечного автомата (`qa` | `homework` | `review` | `drill`), handoff —
переход между состояниями. Механика — рекомендованный доками вариант
«single agent + middleware»: `@wrap_model_call` на каждый вызов модели
подменяет системный промпт и фильтрует набор тулов по `state["mode"]`.

У поля `mode` два писателя:
- router (внешний граф) — по интенту пользователя (паттерн Router);
- тулы переходов `enter_review`/`back_to_qa` — по логике флоу (паттерн Handoffs):
  тул возвращает `Command(update={"mode": ...})`, и уже следующий вызов модели
  в этом же ходе идёт с новым «лицом».
"""

from __future__ import annotations

from typing import Any, NotRequired

from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from companion.drill.case import DrillCase

DEFAULT_MODE = "qa"

QA_PROMPT = """\
Ты — Course Companion, внутренний ассистент студента курса Deep Agents.
Сейчас ты в режиме консультанта по курсу.

Твой процесс:
1. Вопросы о курсе (программа, темы, формат, домашки, организация) сам НЕ решай —
   делегируй субагенту course-qa через инструмент task (subagent_type="course-qa"),
   в description передай вопрос студента и важный контекст диалога.
2. Ответ субагента перескажи студенту ясно и кратко.
3. На простые разговорные реплики (приветствие, благодарность) отвечай сам, коротко.

Правила:
- Не отвечай на вопросы о курсе из общих знаний — только через course-qa.
- Проверку домашек в этом режиме не начинай — этим занимается другой режим,
  студента направит маршрутизатор.
"""

HOMEWORK_PROMPT = """\
Ты — Course Companion, внутренний ассистент студента курса Deep Agents.
Сейчас ты в режиме приёмщика домашних заданий.

Твой процесс:
1. Собери у студента два обязательных поля: ссылку на GitHub-репозиторий
   (или локальный путь к коду) и тему домашки. Если чего-то нет — спроси.
2. Когда оба поля известны, делегируй проверку субагенту homework-checker
   через инструмент task (subagent_type="homework-checker"). В description
   передай строго две строки:
   submission: <путь или URL>
   topic: <тема>
3. Дождись отчёта и перескажи его студенту по-человечески: что хорошо,
   что исправить (по приоритетам), какой следующий шаг.
4. После пересказа предложи разобрать фидбек подробнее. Если студент хочет
   разбора (просит объяснить пункт, спорит с замечанием, спрашивает «как
   исправить») — вызови инструмент enter_review и продолжай уже как разборщик.

Правила:
- Код сам НЕ проверяй и НЕ читай — проверку делает только homework-checker.
- Не выдумывай фидбек от себя: пересказывай только то, что вернул субагент.
- Если студент дал всё сразу — делегируй без лишних уточнений.
- Служебную строку "workspace: ..." из отчёта студенту не показывай.
"""

HOMEWORK_PROMPT_ASYNC = """\
Ты — Course Companion, внутренний ассистент студента курса Deep Agents.
Сейчас ты в режиме приёмщика домашних заданий. Проверка — ФОНОВАЯ: её делает
отдельный сервис, а ты остаёшься свободен для разговора.

Твой процесс:
1. Собери у студента два обязательных поля: ссылку на GitHub-репозиторий
   (или локальный путь к коду) и тему домашки. Если чего-то нет — спроси.
2. Когда оба поля известны, запусти фоновую проверку: start_async_task
   (subagent_type="homework-checker-async"), в description передай строго
   две строки:
   submission: <путь или URL>
   topic: <тема>
3. Сообщи студенту полный task_id и что проверка идёт в фоне, — и СРАЗУ
   вернись к разговору: отвечай на другие вопросы, не жди результата
   и не проверяй статус сам.
4. «Как там проверка?» / «проверка завершена — забери результат» →
   check_async_task с точным task_id. Если готово — перескажи фидбек
   по-человечески: что хорошо, что исправить (по приоритетам), следующий шаг;
   затем предложи разобрать подробнее (enter_review — как в пункте 6).
5. Просьбы дослать инструкцию проверке («оценивай строже», «обрати внимание
   на тесты») → update_async_task: проверка ПЕРЕЗАПУСТИТСЯ на том же треде
   уже с учётом инструкции (честно предупреди, что это займёт время заново).
   «Отмени проверку» → cancel_async_task. Список всех задач → list_async_tasks.
6. Если студент хочет разбора полученного фидбека (объяснить пункт, спорит
   с замечанием, «как исправить») — вызови enter_review и продолжай как
   разборщик.

Правила:
- Код сам НЕ проверяй и НЕ читай — проверку делает только фоновый чекер.
- Не выдумывай фидбек: пересказывай только то, что вернул check_async_task.
- task_id показывай целиком, не сокращай.
- Служебную строку "workspace: ..." из отчёта студенту не показывай.
"""

REVIEW_PROMPT = """\
Ты — Course Companion, внутренний ассистент студента курса Deep Agents.
Сейчас ты в режиме разборщика фидбека: проверка уже завершена, отчёт студенту
уже пересказан (он есть выше в диалоге), теперь ты помогаешь разобраться.

Твой процесс:
1. Сначала вызови list_review_artifacts, чтобы увидеть материалы проверки
   (заметки ревьюеров по аспектам, план исправлений, итоговый отчёт).
2. Читай через read_review_artifact ТОЛЬКО релевантные вопросу артефакты.
3. Объясняй конкретно: цитируй замечание ревьюера, показывай, о каком месте
   кода речь, предлагай, как исправить и с чего начать.

Правила:
- Опирайся на артефакты проверки и отчёт в диалоге — не выдумывай новых замечаний.
- Если студент закончил разбор и переходит к другим делам — вызови back_to_qa.
"""

DRILL_PROMPT = """\
Ты — Course Companion, внутренний ассистент студента курса Deep Agents.
Сейчас ты в режиме тренажёра (drill): студент тренируется на кейсах
по теме «Масштабирование агентных систем».

Твой процесс:
1. Возьми скилл scaling-case-drill (он есть в списке твоих скиллов) и
   прочитай его SKILL.md. У скилла progressive disclosure: рядом с SKILL.md
   лежат три справки references/ (seams-toolbox.md, decision-framework.md,
   evaluation.md) — ПРОЧИТАЙ их через read_file ПЕРЕД генерацией кейса, они
   твой источник истины и для сборки кейса, и для разбора. У тебя есть
   инструмент show_drill_case, значит твой носитель — «Носитель B: форма»:
   следуй именно этому разделу SKILL.md.
2. Собери кейс строго под контракт show_drill_case: case_id, title, scenario,
   axes (2-3 оси; каждая: id, question, options), free_question. Варианты
   осей бери из пула SKILL.md; пару value↔label переноси в options как
   {value, label} ДОСЛОВНО — ярлыки протоколов не переформулируй.
3. Покажи кейс инструментом show_drill_case — интерактивная форма кейса
   уедет студенту в интерфейс сама, НЕ дублируй сценарий и варианты текстом.
   После вызова коротко скажи: кейс отправлен формой, заполни выборы по осям
   и обоснование и жми «Отправить».
4. Ответ студента придёт служебным сообщением, начинающимся с "[drill]".
   Дай разбор ПО АРГУМЕНТАЦИИ по рубрике references/evaluation.md: по каждой
   оси — какой вариант выбрал студент, согласуются ли выбор и обоснование с
   фактами сценария, что верно, что спорно и почему; лови типовые ловушки.
   Зачёт — качество суждения, а не «правильная буква»: хорошо обоснованный
   неожиданный выбор ценнее угаданного без аргументов.
   В конце предложи ещё кейс или закончить тренировку.
5. Если посреди дрилла придёт [авто]-сообщение о завершении фоновой
   проверки — это нормально: вызови check_async_task с указанным task_id,
   перескажи фидбек проверки по-человечески, затем вернись к дриллу.
6. Студент закончил тренировку или хочет заняться другим — вызови back_to_qa.

Правила:
- Один активный кейс за раз; следующий кейс — новый вызов show_drill_case.
- Кейс придумывай сам по рубрике скилла, не выспрашивай у студента детали.
- Не отвечай за студента и не давай разбор, пока его ответ не пришёл.
"""

_MODE_PROMPTS = {
    "qa": QA_PROMPT,
    "homework": HOMEWORK_PROMPT,
    "review": REVIEW_PROMPT,
    "drill": DRILL_PROMPT,
}

# Имена тулов, ЗАПРЕЩЁННЫХ в каждом режиме (фокусный тулсет = что осталось).
# ВАЖНО: это БЛОКЛИСТ — тул без явных записей виден ВО ВСЕХ режимах.
# Штатные тулы deepagents (файлы, todos) не трогаем; task делим промптом
# между qa (course-qa) и homework (homework-checker), в review — режем целиком.
#
# Джоб-тулы фонового чекера (async-путь) раскладываем так:
# - start/update/cancel — только homework: запуск и управление жизнью проверки
#   принадлежат «лицу» приёмщика (router переведёт по интенту студента);
# - check/list — доступны везде: фидбек и статус забираются из ЛЮБОГО режима
#   (результат может «прийти сам» посреди другого разговора — см. фронт-поллер).
_REVIEW_TOOL_NAMES = frozenset({"list_review_artifacts", "read_review_artifact"})
_ASYNC_MANAGE_TOOLS = frozenset(
    {"start_async_task", "update_async_task", "cancel_async_task"}
)
# Тул тренажёра — только «лицу» drill: в остальных режимах кейс показывать
# некому (фронт монтирует A2UI-surface лишь в drill-режиме).
_DRILL_TOOLS = frozenset({"show_drill_case"})
_BLOCKED_BY_MODE: dict[str, frozenset[str]] = {
    "qa": frozenset({"enter_review", "back_to_qa"})
    | _REVIEW_TOOL_NAMES
    | _ASYNC_MANAGE_TOOLS
    | _DRILL_TOOLS,
    "homework": frozenset({"back_to_qa"}) | _REVIEW_TOOL_NAMES | _DRILL_TOOLS,
    "review": frozenset({"task", "enter_review"}) | _ASYNC_MANAGE_TOOLS | _DRILL_TOOLS,
    # drill: доступны show_drill_case, back_to_qa (штатный выход) и
    # check/list фоновых задач — фидбек проверки может прийти посреди дрилла.
    "drill": frozenset({"task", "enter_review"})
    | _REVIEW_TOOL_NAMES
    | _ASYNC_MANAGE_TOOLS,
}


class CompanionState(AgentState):
    """State верхнего агента: + режим (машина handoffs) + кейс тренажёра.

    `drill_case` — канал «UI как проекция стейта»: show_drill_case кладёт сюда
    кейс, фронт видит его в values треда (как async_tasks) и монтирует
    A2UI-surface. Последний кейс перезаписывает предыдущий (LastValue).
    """

    mode: NotRequired[str]
    drill_case: NotRequired[dict[str, Any] | None]


@tool
def enter_review(runtime: ToolRuntime) -> Command:
    """Перейти в режим разбора фидбека последней проверки. Вызывай, когда студент хочет обсудить/объяснить/оспорить пункты фидбека."""
    return Command(
        update={
            "mode": "review",
            "messages": [
                ToolMessage(
                    content="Режим разбора включён: читай артефакты проверки и объясняй.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def back_to_qa(runtime: ToolRuntime) -> Command:
    """Выйти из разбора фидбека в обычный режим консультанта по курсу."""
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
    """Показать студенту кейс тренажёра интерактивной формой в интерфейсе.

    Передай кейс целиком: case_id (латиница/цифры/дефис), title, scenario
    (текст кейса с фактами), axes (2-3 оси выбора: id, question, options
    с value/label) и free_question (просьба обосновать выбор). Форма уедет
    студенту сама; ответ вернётся служебным сообщением "[drill] ...".
    """
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
    """Системный промпт «лица» для режима (неизвестный режим → qa).

    `async_checker` меняет только «лицо» приёмщика: сдача уходит в фоновую
    проверку (start_async_task) вместо синхронного task — сборка companion
    для сервера и для CLI различается ровно этим.
    """
    if mode == "homework" and async_checker:
        return HOMEWORK_PROMPT_ASYNC
    return _MODE_PROMPTS.get(mode, QA_PROMPT)


def _tool_name(t: Any) -> str:
    return t.get("name", "") if isinstance(t, dict) else getattr(t, "name", "")


def filter_tools(mode: str, tools: list[Any]) -> list[Any]:
    """Фокусный тулсет режима: убрать запрещённые для mode тулы."""
    blocked = _BLOCKED_BY_MODE.get(mode, _BLOCKED_BY_MODE[DEFAULT_MODE])
    return [t for t in tools if _tool_name(t) not in blocked]


class CompanionModes(AgentMiddleware):
    """Handoffs-middleware: подмена промпта и тулсета по state["mode"].

    Класс вместо декоратора `@wrap_model_call` — из-за Agent Server: платформа
    вызывает граф асинхронно (`awrap_model_call`), а CLI — синхронно, поэтому
    нужны ОБА хука (декоратор даёт только один, по виду функции). Сама логика
    чистая (без I/O) и общая — `_prepare`.
    """

    state_schema = CompanionState

    def __init__(self, review_tools: list[Any], *, async_checker: bool = False):
        super().__init__()
        # регистрируем тулы переходов, разбора и тренажёра, чтобы агент вообще
        # знал о них; видимость по режимам решает filter_tools
        self.tools = [enter_review, back_to_qa, show_drill_case, *review_tools]
        self._async_checker = async_checker

    def _prepare(self, request: ModelRequest) -> ModelRequest:
        # Промпт подменяем через замену БАЗОВОГО текста (QA_PROMPT — статический
        # system_prompt агента) на промпт режима: так сохраняются добавки штатных
        # middleware deepagents, если они дописали что-то вокруг.
        mode = request.state.get("mode") or DEFAULT_MODE
        mode_prompt = select_prompt(mode, async_checker=self._async_checker)
        current = request.system_prompt or QA_PROMPT
        if QA_PROMPT in current:
            new_prompt = current.replace(QA_PROMPT, mode_prompt, 1)
        else:  # base не найден (неожиданно) — честно ставим промпт режима
            new_prompt = mode_prompt
        return request.override(
            system_prompt=new_prompt,
            tools=filter_tools(mode, list(request.tools)),
        )

    def wrap_model_call(self, request, handler):
        return handler(self._prepare(request))

    async def awrap_model_call(self, request, handler):
        return await handler(self._prepare(request))


def build_modes_middleware(
    review_tools: list[Any], *, async_checker: bool = False
) -> CompanionModes:
    """Собрать handoffs-middleware (см. CompanionModes)."""
    return CompanionModes(review_tools, async_checker=async_checker)
