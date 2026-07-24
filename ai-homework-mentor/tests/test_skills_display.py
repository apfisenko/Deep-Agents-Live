from __future__ import annotations

from rich.console import Console

from homework_mentor.cli.display import render_skills_compact, render_skills_panel
from homework_mentor.skills.models import SkillRef, SkillsSelection


def _sample_skills() -> SkillsSelection:
    return SkillsSelection(
        rubric_skill=SkillRef(
            id="rubric-python-cli",
            path="skills/rubric-python-cli/SKILL.md",
            kind="rubric",
            reason="topic→rubric-python-cli",
        ),
        ecosystem_skills=[
            SkillRef(
                id="modern-python",
                path=".agents/skills/modern-python/SKILL.md",
                kind="ecosystem",
                reason="aspect rule (always_for_aspect)",
                aspect="code_quality",
            ),
        ],
        api_detected=False,
    )


def test_render_skills_panel() -> None:
    console = Console(width=140, record=True)
    render_skills_panel(console, _sample_skills())
    text = console.export_text()
    assert "Rubric & Skills" in text
    assert "rubric-python-cli" in text
    assert "modern-python" in text
    assert "api_detected=False" in text


def test_render_skills_compact() -> None:
    console = Console(width=80, record=True)
    render_skills_compact(console, _sample_skills())
    assert "skills: rubric-python-cli, modern-python" in console.export_text()
