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

_AUTO_INSTALLED = (
    "modern-python",
    "fastapi-templates",
    "uv-package-manager",
    "python-testing-patterns",
    "python-design-patterns",
    "api-design-principles",
)

_ON_DEMAND_INSTALLED = (
    "deep-agents-core",
    "deep-agents-orchestration",
    "deep-agents-memory",
    "langchain-fundamentals",
    "langchain-middleware",
    "ecosystem-primer",
)


def test_code_quality_gets_modern_python() -> None:
    refs = resolve_skills_for_aspect(
        "python-cli",
        "code_quality",
        code_manifest=["main.py", "pkg/utils.py"],
    )
    ids = {ref.id for ref in refs}
    assert "rubric-python-cli" in ids
    assert "modern-python" in ids
    assert "python-design-patterns" in ids
    assert "fastapi-templates" not in ids
    assert "deep-agents-core" not in ids


def test_api_topic_gets_fastapi_and_api_design() -> None:
    refs = resolve_skills_for_aspect(
        "fastapi-api homework",
        "architecture",
        code_manifest=["app/main.py"],
    )
    ids = {ref.id for ref in refs}
    assert "fastapi-templates" in ids
    assert "api-design-principles" in ids
    assert "modern-python" not in ids


def test_api_path_glob_detects_without_topic_keyword() -> None:
    selection = resolve_skills(
        "python homework",
        code_manifest=["app/api/routes.py", "app/main.py"],
    )
    assert selection.api_detected is True
    eco_ids = {ref.id for ref in selection.ecosystem_skills}
    assert "fastapi-templates" in eco_ids
    assert "api-design-principles" in eco_ids


def test_local_hw_without_api_skips_fastapi() -> None:
    selection = resolve_skills(
        "python-cli",
        code_manifest=["main.py", "pkg/__init__.py", "README.md"],
    )
    assert selection.api_detected is False
    assert all(ref.id != "fastapi-templates" for ref in selection.ecosystem_skills)
    assert any(ref.id == "modern-python" for ref in selection.ecosystem_skills)


def test_packaging_and_tests_heuristics() -> None:
    selection = resolve_skills(
        "python-cli",
        code_manifest=["pyproject.toml", "uv.lock", "tests/test_main.py", "main.py"],
    )
    assert selection.packaging_detected is True
    assert selection.tests_detected is True
    eco_ids = {ref.id for ref in selection.ecosystem_skills}
    assert "uv-package-manager" in eco_ids
    assert "python-testing-patterns" in eco_ids


def test_on_demand_not_in_auto_selection() -> None:
    selection = resolve_skills(
        "deep agents homework",
        code_manifest=["src/agent.py", "Dockerfile"],
    )
    assert selection.docker_detected is True
    eco_ids = {ref.id for ref in selection.ecosystem_skills}
    assert "deep-agents-core" not in eco_ids
    assert "langchain-fundamentals" not in eco_ids


def test_path_traversal_skill_id_rejected() -> None:
    with pytest.raises(SkillLoadError, match=r"traversal"):
        resolve_skill_dir("../secrets")


def test_assert_skill_path_outside_allowlist(tmp_path: Path) -> None:
    evil = tmp_path / "SKILL.md"
    evil.write_text("# nope\n", encoding="utf-8")
    with pytest.raises(SkillLoadError, match="outside allowlist"):
        assert_skill_path_allowed(evil)


def test_public_skills_installed() -> None:
    root = project_root() / ".agents" / "skills"
    for skill_id in (*_AUTO_INSTALLED, *_ON_DEMAND_INSTALLED):
        assert (root / skill_id / "SKILL.md").is_file(), skill_id
