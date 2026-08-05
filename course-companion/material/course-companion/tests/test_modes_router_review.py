"""Тесты A2 без LLM: машина режимов, review-тулы, sticky-логика router'а."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

from companion.modes import (
    DEFAULT_MODE,
    DRILL_PROMPT,
    HOMEWORK_PROMPT,
    QA_PROMPT,
    REVIEW_PROMPT,
    filter_tools,
    select_prompt,
    show_drill_case,
)
from companion.review_tools import build_review_tools, find_latest_workspace
from companion.router import build_router_node


class _FakeTool(SimpleNamespace):
    pass


def _tools(*names: str) -> list[_FakeTool]:
    return [_FakeTool(name=n) for n in names]


ALL = ("task", "enter_review", "back_to_qa", "list_review_artifacts",
       "read_review_artifact", "write_todos", "read_file",
       "show_drill_case", "start_async_task", "check_async_task",
       "update_async_task", "cancel_async_task", "list_async_tasks")


def test_select_prompt() -> None:
    assert select_prompt("qa") == QA_PROMPT
    assert select_prompt("homework") == HOMEWORK_PROMPT
    assert select_prompt("review") == REVIEW_PROMPT
    assert select_prompt("drill") == DRILL_PROMPT
    assert select_prompt("garbage") == QA_PROMPT  # неизвестный режим → qa


def test_filter_tools_by_mode() -> None:
    names = lambda ts: {t.name for t in ts}  # noqa: E731
    qa = names(filter_tools("qa", _tools(*ALL)))
    homework = names(filter_tools("homework", _tools(*ALL)))
    review = names(filter_tools("review", _tools(*ALL)))
    drill = names(filter_tools("drill", _tools(*ALL)))

    assert "task" in qa and "enter_review" not in qa and "read_review_artifact" not in qa
    assert {"task", "enter_review"} <= homework and "back_to_qa" not in homework
    assert "task" not in review and "enter_review" not in review
    assert {"back_to_qa", "list_review_artifacts", "read_review_artifact"} <= review
    # show_drill_case виден ТОЛЬКО «лицу» тренажёра
    assert "show_drill_case" in drill
    for modeset in (qa, homework, review):
        assert "show_drill_case" not in modeset
    # drill: без делегирования и управления проверками, но фидбек фоновой
    # проверки забрать можно (может прийти посреди дрилла) и выход штатный
    assert {"back_to_qa", "check_async_task", "list_async_tasks"} <= drill
    assert not {"task", "enter_review", "start_async_task",
                "update_async_task", "cancel_async_task"} & drill
    # штатные тулы deepagents не режутся нигде
    for modeset in (qa, homework, review, drill):
        assert {"write_todos", "read_file"} <= modeset


def test_show_drill_case_writes_state_channel() -> None:
    """Тул кладёт кейс в канал drill_case и отвечает ToolMessage'ем."""
    case = {
        "case_id": "protocol-seams-01",
        "title": "Выбор протокола на шов",
        "scenario": "Чужая команда делает агента биллинга...",
        "axes": [
            {
                "id": "billing_seam",
                "question": "Каким протоколом связать агентов?",
                "options": [
                    {"value": "a2a", "label": "A2A"},
                    {"value": "agent_protocol", "label": "Agent Protocol"},
                ],
            }
        ],
    }
    # ToolRuntime инжектится агентом; в юнит-тесте зовём функцию тула напрямую
    # с двойником рантайма, а сам кейс прогоняем через валидацию контракта.
    from companion.drill import DrillCase

    command = show_drill_case.func(
        case=DrillCase.model_validate(case),
        runtime=SimpleNamespace(tool_call_id="call-1"),
    )
    update = command.update
    assert update["drill_case"]["case_id"] == "protocol-seams-01"
    # дефолт free_question дописан валидацией DrillCase
    assert update["drill_case"]["free_question"]
    (tool_msg,) = update["messages"]
    assert tool_msg.tool_call_id == "call-1"
    assert "drill-protocol-seams-01" in tool_msg.content


def test_find_latest_workspace(tmp_path: Path) -> None:
    assert find_latest_workspace(tmp_path / "нет") is None
    (tmp_path / "20260101-aaa").mkdir()
    (tmp_path / "20260301-ccc").mkdir()
    (tmp_path / "20260201-bbb").mkdir()
    latest = find_latest_workspace(tmp_path)
    assert latest is not None and latest.name == "20260301-ccc"


def test_review_tools(tmp_path: Path) -> None:
    ws = tmp_path / "20260101-abc"
    (ws / "notes").mkdir(parents=True)
    (ws / "output").mkdir()
    (ws / "notes" / "quality.md").write_text("замечание", encoding="utf-8")
    (ws / "output" / "fix_plan.md").write_text("план", encoding="utf-8")
    list_tool, read_tool = build_review_tools(tmp_path)

    listing = list_tool.invoke({})
    assert "notes/quality.md" in listing and "output/fix_plan.md" in listing
    assert read_tool.invoke({"filename": "notes/quality.md"}) == "замечание"
    assert "Ошибка" in read_tool.invoke({"filename": "../secrets.md"})
    assert "Ошибка" in read_tool.invoke({"filename": "notes/нет.md"})


def test_review_tools_empty(tmp_path: Path) -> None:
    list_tool, read_tool = build_review_tools(tmp_path / "пусто")
    assert "Ошибка" in list_tool.invoke({})
    assert "Ошибка" in read_tool.invoke({"filename": "x.md"})


class _FakeStructured:
    def __init__(self, decision: str, fail: bool = False) -> None:
        self._decision, self._fail = decision, fail
        self.last_prompt = ""

    def invoke(self, messages):
        if self._fail:
            raise RuntimeError("boom")
        self.last_prompt = str(messages)
        return SimpleNamespace(decision=self._decision)

    def with_config(self, _config):
        # router вешает тег nostream (companion/router.py) — двойник повторяет
        # runnable-интерфейс, сам конфиг для логики теста не важен
        return self


class _FakeModel:
    def __init__(self, structured: _FakeStructured) -> None:
        self._structured = structured

    def with_structured_output(self, _schema):
        return self._structured


def _route(decision: str, mode: str | None, fail: bool = False) -> str:
    node = build_router_node(_FakeModel(_FakeStructured(decision, fail)))
    state = {
        "messages": [AIMessage(content="ок"), HumanMessage(content="сообщение")],
    }
    if mode:
        state["mode"] = mode
    return node(state)["mode"]


def test_router_decisions() -> None:
    assert _route("qa", None) == "qa"
    assert _route("homework", "qa") == "homework"
    assert _route("stay", "homework") == "homework"  # sticky: stay не трогает режим
    assert _route("stay", "review") == "review"
    assert _route("qa", "review") == "qa"  # явная смена темы выводит из review
    # категория тренажёра: вход по интенту, sticky внутри, штатный выход в qa
    assert _route("drill", "qa") == "drill"
    assert _route("drill", "homework") == "drill"
    assert _route("stay", "drill") == "drill"
    assert _route("qa", "drill") == "qa"


def test_router_failure_is_stay() -> None:
    assert _route("qa", "homework", fail=True) == "homework"
    assert _route("qa", None, fail=True) == DEFAULT_MODE


def test_router_service_messages_never_switch_mode() -> None:
    """[авто]/[drill] — транспорт результата, не интент: режим не трогаем
    (иначе фидбек проверки мог бы выбить из drill посреди формы)."""
    structured = _FakeStructured("homework")  # даже если бы LLM ошибся —
    node = build_router_node(_FakeModel(structured))
    for prefix in ("[авто]", "[drill]"):
        state = {
            "mode": "drill",
            "messages": [HumanMessage(content=f"{prefix} проверка завершена")],
        }
        assert node(state)["mode"] == "drill"
    assert structured.last_prompt == ""  # классификатор даже не вызывался
