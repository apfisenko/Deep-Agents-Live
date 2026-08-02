"""Unit-тесты Router с mock LLM — без реальных вызовов к API."""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from course_companion.router.intent import Intent, RouterInput
from course_companion.router.router import route


def _make_mock_llm(return_value: Intent) -> MagicMock:
    """Mock LLM, чей with_structured_output().invoke() возвращает заданный Intent."""
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = return_value
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm


def _make_broken_llm() -> MagicMock:
    """Mock LLM, чей invoke() бросает RuntimeError."""
    mock_structured = MagicMock()
    mock_structured.invoke.side_effect = RuntimeError("API error")
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm


def test_homework_intent() -> None:
    mock = _make_mock_llm(Intent(decision="homework"))
    result = route(
        RouterInput(recent_messages=["хочу сдать ДЗ"], current_mode="qa"),
        llm=mock,
    )
    assert result.decision == "homework"


def test_qa_intent() -> None:
    mock = _make_mock_llm(Intent(decision="qa"))
    result = route(
        RouterInput(recent_messages=["расскажи о теме 3"], current_mode="qa"),
        llm=mock,
    )
    assert result.decision == "qa"


def test_stay_intent() -> None:
    mock = _make_mock_llm(Intent(decision="stay"))
    result = route(
        RouterInput(recent_messages=["да, подтверждаю"], current_mode="homework"),
        llm=mock,
    )
    assert result.decision == "stay"


def test_failsafe() -> None:
    """При сбое LLM route() не должен поднимать исключение — только вернуть stay."""
    broken = _make_broken_llm()
    # Не должно бросить исключение:
    result = route(
        RouterInput(recent_messages=["что-то непонятное"], current_mode="qa"),
        llm=broken,
    )
    assert result.decision == "stay"


def test_review_not_in_literal() -> None:
    """`review` запрещён в Intent: это состояние флоу, не интент пользователя."""
    with pytest.raises(ValidationError):
        Intent(decision="review")  # type: ignore[arg-type]
