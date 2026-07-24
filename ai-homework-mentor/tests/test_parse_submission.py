from __future__ import annotations

from pathlib import Path

from homework_mentor.config import load_yaml_config, project_root
from homework_mentor.submission import SourceType, parse_submission


def test_github_url_and_topic_heuristic() -> None:
    text = "Проверь https://github.com/student/hw-fastapi-bot тема: FastAPI + Telegram bot"
    sub = parse_submission(text)
    assert sub.source_type is SourceType.GITHUB_URL
    assert sub.source_value == "https://github.com/student/hw-fastapi-bot"
    assert sub.topic == "FastAPI + Telegram bot"
    assert sub.needs_clarification is False
    assert sub.clarification_question is None


def test_github_url_without_topic_asks_clarification() -> None:
    text = "проверь https://github.com/org/tiny-repo пожалуйста"
    sub = parse_submission(text, topic_extractor=lambda _t: None)
    assert sub.source_type is SourceType.GITHUB_URL
    assert sub.topic is None
    assert sub.needs_clarification is True
    assert sub.clarification_question is not None
    assert "тему" in sub.clarification_question.lower()


def test_incomplete_input_no_source_no_topic() -> None:
    sub = parse_submission("проверь моё дз пожалуйста", topic_extractor=lambda _t: None)
    assert sub.source_type is SourceType.UNKNOWN
    assert sub.source_value is None
    assert sub.topic is None
    assert sub.needs_clarification is True
    assert "GitHub" in (sub.clarification_question or "")


def test_explicit_path_sets_local_source(tmp_path: Path) -> None:
    sub = parse_submission(
        "Тема: LangGraph agents",
        explicit_path=tmp_path,
        topic_extractor=lambda _t: None,
    )
    assert sub.source_type is SourceType.LOCAL_PATH
    assert sub.source_value == str(tmp_path)
    assert sub.topic == "LangGraph agents"
    assert sub.needs_clarification is False


def test_does_not_invent_topic_from_extractor() -> None:
    sub = parse_submission(
        "https://github.com/a/b",
        topic_extractor=lambda _t: None,
    )
    assert sub.topic is None
    assert sub.needs_clarification is True


def test_parse_prompt_loaded_from_yaml() -> None:
    cfg = load_yaml_config()
    prompt = cfg.parse_submission_prompts.system_prompt
    assert "topic" in prompt.lower() or "тему" in prompt.lower() or "extract" in prompt.lower()
    assert (project_root() / "config" / "prompts" / "parse_submission.yaml").is_file()
