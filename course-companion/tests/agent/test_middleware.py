"""Unit-тесты middleware конечного автомата режимов."""

import pytest

from course_companion.agent.middleware import (
    MODE_PROMPTS,
    filter_tools,
    select_prompt,
)
from course_companion.agent.tools import ALL_TOOLS


def test_select_prompt() -> None:
    qa = select_prompt("qa")
    hw = select_prompt("homework")
    rv = select_prompt("review")

    assert len(qa) > 0
    assert len(hw) > 0
    assert len(rv) > 0
    assert qa != hw
    assert hw != rv
    assert qa != rv


def test_select_prompt_unknown_mode() -> None:
    with pytest.raises(KeyError, match="unknown_mode"):
        select_prompt("unknown_mode")


def test_select_prompt_covers_all_modes() -> None:
    for mode in MODE_PROMPTS:
        assert select_prompt(mode)


def test_filter_tools_qa() -> None:
    result = filter_tools("qa", ALL_TOOLS)
    names = {t.__name__ for t in result}
    assert "run_homework_check" not in names
    assert "complete_homework" not in names
    assert "explain_feedback" not in names


def test_filter_tools_review() -> None:
    result = filter_tools("review", ALL_TOOLS)
    names = {t.__name__ for t in result}
    assert "ask_course_qa" not in names
    assert "switch_to_homework" not in names
    assert "run_homework_check" not in names


def test_filter_tools_homework() -> None:
    result = filter_tools("homework", ALL_TOOLS)
    names = {t.__name__ for t in result}
    assert "explain_feedback" not in names
    assert "show_fix_plan" not in names
    assert "ask_course_qa" not in names


def test_filter_tools_unknown_mode() -> None:
    with pytest.raises(KeyError, match="bad_mode"):
        filter_tools("bad_mode", ALL_TOOLS)
