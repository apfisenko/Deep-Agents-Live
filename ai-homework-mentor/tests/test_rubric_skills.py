from __future__ import annotations

from pathlib import Path

from homework_mentor.config import project_root
from homework_mentor.skills.loader import load_skill
from homework_mentor.skills.router import resolve_skills
from homework_mentor.workspace import create_session


def test_python_cli_topic_maps_to_rubric_skill() -> None:
    selection = resolve_skills("Тема: python-cli", code_manifest=["main.py", "pkg/cli.py"])
    assert selection.rubric_skill.id == "rubric-python-cli"
    assert (project_root() / "skills" / "rubric-python-cli" / "SKILL.md").is_file()
    loaded = load_skill("rubric-python-cli")
    assert "cli-entry" in loaded.body


def test_unknown_topic_uses_default_rubric_skill() -> None:
    selection = resolve_skills("random topic", code_manifest=["a.py"])
    assert selection.rubric_skill.id == "rubric-default"


def test_copy_rubric_skill_into_session(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="skills-test")
    selection = resolve_skills("python-cli", code_manifest=["main.py"], session=session)
    active = session.rubric_dir / "active_skill.md"
    assert active.is_file()
    assert selection.rubric_skill.id == "rubric-python-cli"
    assert "Python CLI" in active.read_text(encoding="utf-8")
