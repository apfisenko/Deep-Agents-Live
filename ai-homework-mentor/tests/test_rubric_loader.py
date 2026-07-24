from __future__ import annotations

from pathlib import Path

from homework_mentor.rubric.loader import load_rubric_templates, select_rubric
from homework_mentor.workspace import create_session


def test_select_known_topic() -> None:
    selection = select_rubric("Тема: python-cli")
    assert selection.template_name == "python-cli"
    assert selection.used_default is False
    assert selection.rubric.id == "python-cli"


def test_select_unknown_topic_uses_default() -> None:
    selection = select_rubric("totally-unknown-topic")
    assert selection.template_name == "default"
    assert selection.used_default is True


def test_active_yaml_in_session(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="rubric-session")
    selection = select_rubric("python-cli", session=session)
    assert selection.active_path is not None
    assert selection.active_path.is_file()
    assert selection.active_path.parent.name == "rubric"


def test_templates_include_default() -> None:
    templates = load_rubric_templates()
    assert "default" in templates
    assert "python-cli" in templates
