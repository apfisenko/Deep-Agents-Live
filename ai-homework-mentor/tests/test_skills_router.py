from __future__ import annotations

from pathlib import Path

import pytest

from homework_mentor.config import project_root
from homework_mentor.skills.loader import (
    SkillLoadError,
    assert_skill_path_allowed,
    resolve_skill_dir,
)
from homework_mentor.skills.router import resolve_skills, resolve_skills_for_aspect


def test_code_quality_gets_modern_python() -> None:
    refs = resolve_skills_for_aspect(
        "python-cli",
        "code_quality",
        code_manifest=["main.py", "pkg/utils.py"],
    )
    ids = {ref.id for ref in refs}
    assert "rubric-python-cli" in ids
    assert "modern-python" in ids
    assert "fastapi-templates" not in ids


def test_api_topic_gets_fastapi_templates_on_architecture() -> None:
    refs = resolve_skills_for_aspect(
        "fastapi-api homework",
        "architecture",
        code_manifest=["app/main.py"],
    )
    ids = {ref.id for ref in refs}
    assert "fastapi-templates" in ids
    assert "modern-python" not in ids  # different aspect


def test_api_path_glob_detects_without_topic_keyword() -> None:
    selection = resolve_skills(
        "python homework",
        code_manifest=["app/api/routes.py", "app/main.py"],
    )
    assert selection.api_detected is True
    eco_ids = {ref.id for ref in selection.ecosystem_skills}
    assert "fastapi-templates" in eco_ids


def test_local_hw_without_api_skips_fastapi() -> None:
    selection = resolve_skills(
        "python-cli",
        code_manifest=["main.py", "pkg/__init__.py", "README.md"],
    )
    assert selection.api_detected is False
    assert all(ref.id != "fastapi-templates" for ref in selection.ecosystem_skills)
    assert any(ref.id == "modern-python" for ref in selection.ecosystem_skills)


def test_path_traversal_skill_id_rejected() -> None:
    with pytest.raises(SkillLoadError, match=r"traversal"):
        resolve_skill_dir("../secrets")


def test_assert_skill_path_outside_allowlist(tmp_path: Path) -> None:
    evil = tmp_path / "SKILL.md"
    evil.write_text("# nope\n", encoding="utf-8")
    with pytest.raises(SkillLoadError, match="outside allowlist"):
        assert_skill_path_allowed(evil)


def test_public_skills_installed() -> None:
    assert (project_root() / ".agents" / "skills" / "modern-python" / "SKILL.md").is_file()
    assert (project_root() / ".agents" / "skills" / "fastapi-templates" / "SKILL.md").is_file()
