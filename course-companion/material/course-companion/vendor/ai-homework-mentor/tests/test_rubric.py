from pathlib import Path

import pytest

from mentor.agent.tools.rubric import _load_rubric, select_rubric
from mentor.agent.tools.skills_loader import (
    ALLOWED_PUBLIC_SKILLS,
    SkillPlan,
    build_skill_plan,
    load_skill_text,
)
from mentor.agent.tools.workspace import Workspace
from mentor.config import CONFIG_DIR, get_config


def test_fastapi_rubric_has_skills() -> None:
    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")
    assert rubric.rubric_skill == "rubric-fastapi"
    assert rubric.aspect_skills["api-design"] == ["fastapi-templates"]
    assert rubric.aspect_skills["code-quality"] == ["modern-python"]


def test_select_rubric_fastapi_topic() -> None:
    config = get_config()
    rubric = select_rubric(config, "FastAPI REST API")
    assert rubric.topic == "fastapi"


def test_build_skill_plan() -> None:
    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")
    plan = build_skill_plan(rubric)
    assert plan.rubric_skill == "rubric-fastapi"
    assert "fastapi-templates" in plan.by_aspect["api-design"]


def test_load_public_skill() -> None:
    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")
    text = load_skill_text("modern-python")
    assert "name:" in text or "#" in text
    rubric_text = load_skill_text("rubric-fastapi", rubric=rubric)
    assert "FastAPI" in rubric_text


def test_load_skill_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="allowed"):
        load_skill_text("evil-skill")


def test_materialize_workspace_skills(tmp_path: Path) -> None:
    from mentor.agent.tools.skills_loader import materialize_workspace_skills

    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "python-cli.yaml")
    workspace = Workspace(root=tmp_path)
    workspace.ensure_layout()
    plan = materialize_workspace_skills(workspace, rubric)
    assert isinstance(plan, SkillPlan)
    assert len(plan.materialized) >= 2
    assert (workspace.skills_dir / plan.rubric_skill / "SKILL.md").exists()
    assert (workspace.skills_dir / "modern-python" / "SKILL.md").exists()
    names = {m.name for m in plan.materialized}
    assert plan.rubric_skill in names
    assert "modern-python" in names
    for skill in plan.materialized:
        assert skill.source_path.exists()
        assert skill.workspace_path.exists()
        assert skill.size_bytes > 0


def test_allowed_public_skills_include_required() -> None:
    assert "fastapi-templates" in ALLOWED_PUBLIC_SKILLS
    assert "docker-expert" in ALLOWED_PUBLIC_SKILLS
    assert "deep-agents-core" in ALLOWED_PUBLIC_SKILLS


def test_deep_agents_rubric_materialize(tmp_path: Path) -> None:
    from mentor.agent.tools.skills_loader import materialize_workspace_skills

    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "deep-agents.yaml")
    workspace = Workspace(root=tmp_path)
    workspace.ensure_layout()
    plan = materialize_workspace_skills(workspace, rubric)
    names = {m.name for m in plan.materialized}
    assert "rubric-deep-agents" in names
    assert "deep-agents-orchestration" in names
    assert "langchain-middleware" in names
