"""Smoke-тесты Sprint 01: базовые импорты без ошибок."""

from course_companion import __version__
from mentor.agent.orchestrator import MentorOrchestrator


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_mentor_import() -> None:
    assert MentorOrchestrator is not None
