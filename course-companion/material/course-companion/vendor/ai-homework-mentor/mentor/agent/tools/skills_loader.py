"""Load and materialize trusted skills for reviewer subagents (S05)."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from mentor.agent.tools.rubric import Rubric
from mentor.agent.tools.workspace import Workspace
from mentor.config import PROJECT_ROOT

ALLOWED_PUBLIC_SKILLS = frozenset(
    {
        "fastapi-templates",
        "modern-python",
        "docker-expert",
        "python-design-patterns",
        "api-design-principles",
        "python-testing-patterns",
        "deep-agents-core",
        "deep-agents-orchestration",
        "deep-agents-memory",
        "langchain-middleware",
        "langchain-fundamentals",
        "ecosystem-primer",
        "uv-package-manager",
    }
)

REPO_SKILLS_ROOT = PROJECT_ROOT.parent / ".agents" / "skills"
PROJECT_RUBRIC_SKILLS_ROOT = PROJECT_ROOT / "skills" / "rubrics"
_SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class MaterializedSkill:
    name: str
    source_path: Path
    workspace_path: Path
    size_bytes: int


@dataclass(frozen=True)
class SkillPlan:
    rubric_skill: str
    by_aspect: dict[str, list[str]] = field(default_factory=dict)
    materialized: tuple[MaterializedSkill, ...] = ()

    def skills_for_aspect(self, aspect_id: str) -> list[str]:
        return list(self.by_aspect.get(aspect_id, []))

    def virtual_paths_for_aspect(self, aspect_id: str) -> list[str]:
        names = [self.rubric_skill, *self.skills_for_aspect(aspect_id)]
        unique: list[str] = []
        seen: set[str] = set()
        for name in names:
            if name not in seen:
                seen.add(name)
                unique.append(f"/skills/{name}")
        return unique


def _validate_skill_name(name: str) -> str:
    if not _SKILL_NAME_RE.match(name):
        msg = f"Invalid skill name: {name!r}"
        raise ValueError(msg)
    return name


def _public_skill_path(skill_name: str) -> Path:
    _validate_skill_name(skill_name)
    if skill_name not in ALLOWED_PUBLIC_SKILLS:
        msg = f"Skill {skill_name!r} is not in the allowed public skills list"
        raise ValueError(msg)
    path = (REPO_SKILLS_ROOT / skill_name / "SKILL.md").resolve()
    if not path.is_relative_to(REPO_SKILLS_ROOT.resolve()):
        msg = f"Skill path escapes trusted root: {path}"
        raise ValueError(msg)
    if not path.exists():
        msg = f"Public skill not found: {path}"
        raise FileNotFoundError(msg)
    return path


def _rubric_skill_path(rubric: Rubric) -> Path:
    skill_name = _validate_skill_name(rubric.rubric_skill)
    path = (PROJECT_RUBRIC_SKILLS_ROOT / rubric.topic / "SKILL.md").resolve()
    if not path.is_relative_to(PROJECT_RUBRIC_SKILLS_ROOT.resolve()):
        msg = f"Rubric skill path escapes trusted root: {path}"
        raise ValueError(msg)
    if not path.exists():
        topic_dir = skill_name.removeprefix("rubric-")
        alt = (PROJECT_RUBRIC_SKILLS_ROOT / topic_dir / "SKILL.md").resolve()
        if alt.exists():
            return alt
        msg = f"Rubric skill not found for topic {rubric.topic}: {path}"
        raise FileNotFoundError(msg)
    return path


def load_skill_text(skill_name: str, *, rubric: Rubric | None = None) -> str:
    """Load SKILL.md text from trusted locations only."""
    if skill_name.startswith("rubric-"):
        if rubric is None:
            msg = "Rubric context required for rubric skills"
            raise ValueError(msg)
        path = _rubric_skill_path(rubric)
    else:
        path = _public_skill_path(skill_name)
    return path.read_text(encoding="utf-8")


def build_skill_plan(rubric: Rubric) -> SkillPlan:
    by_aspect: dict[str, list[str]] = {}
    for aspect in rubric.aspects:
        aspect_id = str(aspect.get("id", "aspect"))
        raw = rubric.aspect_skills.get(aspect_id, ["modern-python"])
        names = [_validate_skill_name(str(n)) for n in raw]
        for name in names:
            if not name.startswith("rubric-") and name not in ALLOWED_PUBLIC_SKILLS:
                msg = f"Disallowed skill {name!r} for aspect {aspect_id}"
                raise ValueError(msg)
        by_aspect[aspect_id] = names
    return SkillPlan(rubric_skill=rubric.rubric_skill, by_aspect=by_aspect)


def _copy_skill_md(source: Path, dest_dir: Path) -> MaterializedSkill:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "SKILL.md"
    shutil.copy2(source, dest_file)
    return MaterializedSkill(
        name=dest_dir.name,
        source_path=source,
        workspace_path=dest_file,
        size_bytes=dest_file.stat().st_size,
    )


def materialize_workspace_skills(workspace: Workspace, rubric: Rubric) -> SkillPlan:
    """Copy rubric + public SKILL.md files into workspace for DeepAgents skills middleware."""
    plan = build_skill_plan(rubric)
    skills_root = workspace.skills_dir
    skills_root.mkdir(parents=True, exist_ok=True)

    materialized: list[MaterializedSkill] = []
    rubric_src = _rubric_skill_path(rubric)
    materialized.append(_copy_skill_md(rubric_src, skills_root / plan.rubric_skill))

    copied_public: set[str] = set()
    for names in plan.by_aspect.values():
        for skill_name in names:
            if skill_name in copied_public or skill_name.startswith("rubric-"):
                continue
            public_src = _public_skill_path(skill_name)
            materialized.append(_copy_skill_md(public_src, skills_root / skill_name))
            copied_public.add(skill_name)

    workspace.write_text(
        skills_root / "manifest.md",
        "# Skills manifest\n\n"
        f"- Rubric skill: `{plan.rubric_skill}`\n"
        + "".join(
            f"- `{aspect}`: {', '.join(f'`{s}`' for s in skills)}\n"
            for aspect, skills in plan.by_aspect.items()
        ),
    )
    return SkillPlan(
        rubric_skill=plan.rubric_skill,
        by_aspect=plan.by_aspect,
        materialized=tuple(materialized),
    )
