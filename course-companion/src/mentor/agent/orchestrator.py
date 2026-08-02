"""MentorOrchestrator — адаптер над homework_mentor.orchestrator."""

from __future__ import annotations

from homework_mentor.orchestrator import ReviewRunResult, run_review
from homework_mentor.pipeline import run_homework_session


class MentorOrchestrator:
    """Точка входа в homework_mentor для course-companion.

    Принимает rubric (тема/рубрика) и workspace (путь к ДЗ),
    запускает полный пайплайн проверки и возвращает ReviewRunResult.
    """

    run_review = staticmethod(run_review)

    def __init__(self, *, rubric: str, workspace: str) -> None:
        self.rubric = rubric
        self.workspace = workspace

    def run(self) -> ReviewRunResult:
        """Запустить проверку ДЗ и вернуть результат."""
        result = run_homework_session(
            raw_text=self.workspace,
            explicit_path=self.workspace,
            topic_extractor=lambda _: self.rubric,
        )
        review = result.review
        if result.kind == "clarification" or review is None:
            msg = f"[mentor] pipeline produced no review for workspace={self.workspace!r}"
            raise RuntimeError(msg)
        return review
