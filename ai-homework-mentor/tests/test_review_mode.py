"""S8 Task 01: ReviewMode resolve + wiring single vs subagents."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from homework_mentor.cli.app import build_parser
from homework_mentor.code_fetch.models import FetchResult
from homework_mentor.config import (
    ConfigError,
    RuntimeSettings,
    load_yaml_config,
    project_root,
    resolve_review_mode,
)
from homework_mentor.orchestrator.review import (
    ReviewRunResult,
    build_review_agent,
    build_review_message,
)
from homework_mentor.output.schemas import CoverageReport, FinalFeedback, FixPlan, StrengthItem
from homework_mentor.pipeline import run_homework_session
from homework_mentor.reviewers.notes import materialize_single_agent_note_from_reply
from homework_mentor.reviewers.window_metrics import ReviewerWindowMetricsCollector
from homework_mentor.rubric.loader import select_rubric
from homework_mentor.submission import SourceType
from homework_mentor.submission.models import Submission
from homework_mentor.workspace import create_session


def test_resolve_review_mode_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REVIEW_MODE", raising=False)
    assert resolve_review_mode(None) == "subagents"
    assert resolve_review_mode("") == "subagents"


def test_resolve_review_mode_cli_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REVIEW_MODE", "subagents")
    assert resolve_review_mode("single") == "single"


def test_resolve_review_mode_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REVIEW_MODE", "single")
    assert resolve_review_mode(None) == "single"


def test_resolve_review_mode_invalid() -> None:
    with pytest.raises(ConfigError, match="Invalid review mode"):
        resolve_review_mode("parallel")


def test_build_review_message_single_uses_single_template(tmp_path: Path) -> None:
    prompts = load_yaml_config().review_prompts
    session = create_session(root=tmp_path, session_id="msg")
    submission = Submission(
        source_type=SourceType.LOCAL_PATH,
        source_value=str(tmp_path),
        topic="python-cli",
        raw_text="Тема: python-cli",
    )
    fetch = FetchResult(
        source="local",
        staging_dir=session.code_dir,
        files=["main.py"],
    )
    rubric = select_rubric("python-cli", session=session)
    message = build_review_message(
        submission=submission,
        fetch=fetch,
        rubric=rubric,
        prompts=prompts,
        review_mode="single",
    )
    assert "single agent" in message.lower()
    assert "review_architecture.md" in message


def test_build_review_agent_single_skips_subagents(tmp_path: Path) -> None:
    runtime = RuntimeSettings(
        yaml=load_yaml_config(),
        openrouter_api_key=SecretStr("test-key"),
    )
    captured: dict[str, object] = {}

    def fake_create_deep_agent(**kwargs: object) -> MagicMock:
        captured.update(kwargs)
        return MagicMock()

    with (
        patch(
            "homework_mentor.orchestrator.review.init_openrouter_chat_model",
            return_value=MagicMock(),
        ),
        patch(
            "homework_mentor.orchestrator.review.create_deep_agent",
            side_effect=fake_create_deep_agent,
        ),
        patch("homework_mentor.orchestrator.review._register_review_harness"),
        patch(
            "homework_mentor.orchestrator.review.set_pending_summarization_middleware",
        ),
        patch(
            "homework_mentor.orchestrator.review.build_summarization_middleware",
            return_value=MagicMock(),
        ),
        patch("homework_mentor.orchestrator.review.apply_openrouter_process_env"),
    ):
        build_review_agent(runtime, session_root=tmp_path, review_mode="single")

    assert captured.get("subagents") == []
    assert "single-agent" in str(captured.get("system_prompt", "")).lower()


def test_build_review_agent_subagents_registers_reviewers(tmp_path: Path) -> None:
    runtime = RuntimeSettings(
        yaml=load_yaml_config(),
        openrouter_api_key=SecretStr("test-key"),
    )
    captured: dict[str, object] = {}

    def fake_create_deep_agent(**kwargs: object) -> MagicMock:
        captured.update(kwargs)
        return MagicMock()

    with (
        patch(
            "homework_mentor.orchestrator.review.init_openrouter_chat_model",
            return_value=MagicMock(),
        ),
        patch(
            "homework_mentor.orchestrator.review.create_deep_agent",
            side_effect=fake_create_deep_agent,
        ),
        patch("homework_mentor.orchestrator.review._register_review_harness"),
        patch(
            "homework_mentor.orchestrator.review.set_pending_summarization_middleware",
        ),
        patch(
            "homework_mentor.orchestrator.review.build_summarization_middleware",
            return_value=MagicMock(),
        ),
        patch("homework_mentor.orchestrator.review.apply_openrouter_process_env"),
    ):
        build_review_agent(
            runtime,
            session_root=tmp_path,
            review_mode="subagents",
            window_metrics=ReviewerWindowMetricsCollector(),
        )

    subagents = captured.get("subagents")
    assert isinstance(subagents, list)
    assert len(subagents) >= 2
    for item in subagents:
        assert isinstance(item, dict)
        assert item.get("middleware")


def test_pipeline_passes_review_mode(tmp_path: Path) -> None:
    fixture = project_root() / "tests" / "fixtures" / "local_hw"
    session = create_session(root=tmp_path, session_id="mode-pipe")
    seen: dict[str, object] = {}

    def review_runner(**kwargs: object) -> ReviewRunResult:
        seen["review_mode"] = kwargs.get("review_mode")
        return ReviewRunResult(
            reply="ok",
            review_mode="single",
            final_feedback=FinalFeedback(
                coverage=CoverageReport(
                    aspects_expected=["architecture"],
                    aspects_covered=["architecture"],
                    gaps=[],
                ),
                strengths=[StrengthItem(text="ok")],
                issues=[],
                next_step="done",
            ),
            fix_plan=FixPlan(),
        )

    result = run_homework_session(
        raw_text="Тема: python-cli",
        explicit_path=fixture,
        topic_extractor=lambda _t: "python-cli",
        use_llm_topic=False,
        session_factory=lambda: session,
        review_runner=review_runner,
        review_mode="single",
    )
    assert result.kind == "ok"
    assert result.review_mode == "single"
    assert seen["review_mode"] == "single"


def test_cli_invalid_mode_exits() -> None:
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["-Message", "Тема: x", "-Mode", "parallel"])
    assert exc.value.code == 2


def test_materialize_single_agent_note(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="single-note")
    path = materialize_single_agent_note_from_reply(session, "Architecture looks fine.")
    assert path is not None
    assert path.name == "review_single.md"
    assert "Architecture" in path.read_text(encoding="utf-8")
    assert materialize_single_agent_note_from_reply(session, "ignored") is None
