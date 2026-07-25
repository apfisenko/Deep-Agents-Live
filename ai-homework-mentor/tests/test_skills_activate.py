"""S8 Task 08: mid-run skill activation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from homework_mentor.skills import (
    SkillActivateError,
    activate_skill,
    resolve_skills,
)
from homework_mentor.skills.activate import build_activate_review_skill_tool
from homework_mentor.workspace import create_session


def test_activate_on_demand_skill(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="act01")
    selection = resolve_skills("python-cli", code_manifest=["main.py"])
    assert all(ref.id != "deep-agents-core" for ref in selection.ecosystem_skills)

    by_aspect: dict[str, list] = {"architecture": []}
    ref = activate_skill(
        selection,
        "deep-agents-core",
        "architecture",
        "agent harness in submission",
        session=session,
        skills_by_aspect=by_aspect,
    )
    assert ref.source == "on_demand"
    assert any(item.id == "deep-agents-core" for item in selection.ecosystem_skills)
    assert by_aspect["architecture"][0].id == "deep-agents-core"

    trace = session.notes_dir / "skills_trace.jsonl"
    assert trace.is_file()
    line = json.loads(trace.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert line["skill_id"] == "deep-agents-core"
    assert line["source"] == "on_demand"
    excerpt = session.notes_dir / "skills" / "deep-agents-core.md"
    assert excerpt.is_file()


def test_activate_idempotent(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="act02")
    selection = resolve_skills("python-cli", code_manifest=["main.py"])
    first = activate_skill(
        selection,
        "langchain-fundamentals",
        "architecture",
        "uses langchain",
        session=session,
    )
    second = activate_skill(
        selection,
        "langchain-fundamentals",
        "architecture",
        "uses langchain again",
        session=session,
    )
    assert first.id == second.id
    assert selection.on_demand_count() == 1


def test_activate_unknown_skill_fails() -> None:
    selection = resolve_skills("python-cli", code_manifest=["main.py"])
    with pytest.raises(SkillActivateError, match="catalog"):
        activate_skill(selection, "not-a-real-skill", "architecture", "nope")


def test_activate_wrong_aspect_fails() -> None:
    selection = resolve_skills("python-cli", code_manifest=["main.py"])
    with pytest.raises(SkillActivateError, match="aspect"):
        activate_skill(selection, "deep-agents-core", "code_quality", "wrong aspect")


def test_activate_tool_returns_error_string(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="act03")
    selection = resolve_skills("python-cli", code_manifest=["main.py"])
    tool = build_activate_review_skill_tool(selection, session=session)
    result = tool.invoke(
        {"skill_id": "missing-skill", "aspect": "architecture", "reason": "test"},
    )
    assert result.startswith("ERROR:")
