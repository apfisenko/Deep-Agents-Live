"""Load SKILL.md files from allowlisted project paths."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from homework_mentor.config import project_root

if TYPE_CHECKING:
    from homework_mentor.workspace.session import WorkspaceSession

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


class SkillLoadError(RuntimeError):
    """Invalid skill path or missing SKILL.md."""


@dataclass(frozen=True)
class LoadedSkill:
    skill_id: str
    path: Path
    body: str
    name: str
    description: str


def allowlist_roots(*, root: Path | None = None) -> tuple[Path, Path]:
    base = root or project_root()
    return (base / "skills").resolve(), (base / ".agents" / "skills").resolve()


def resolve_skill_dir(skill_id: str, *, root: Path | None = None) -> Path:
    """Resolve skill directory by id under allowlisted roots."""
    if ".." in Path(skill_id).parts or Path(skill_id).is_absolute():
        msg = f"Skill id path traversal rejected: {skill_id}"
        raise SkillLoadError(msg)
    project_skills, agents_skills = allowlist_roots(root=root)
    candidates = (
        project_skills / skill_id,
        agents_skills / skill_id,
    )
    for candidate in candidates:
        skill_md = candidate / "SKILL.md"
        if skill_md.is_file():
            _assert_under_allowlist(skill_md, root=root)
            return candidate.resolve()
    msg = f"Skill not found in allowlist roots: {skill_id}"
    raise SkillLoadError(msg)


def assert_skill_path_allowed(path: Path, *, root: Path | None = None) -> Path:
    """Validate an arbitrary path is an allowlisted SKILL.md; raise otherwise."""
    resolved = path.resolve()
    _assert_under_allowlist(resolved, root=root)
    if resolved.name != "SKILL.md" or not resolved.is_file():
        msg = f"Not an allowlisted SKILL.md: {resolved}"
        raise SkillLoadError(msg)
    return resolved


def load_skill(skill_id: str, *, root: Path | None = None) -> LoadedSkill:
    skill_dir = resolve_skill_dir(skill_id, root=root)
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    name, description, body = _parse_frontmatter(text, skill_id=skill_id)
    return LoadedSkill(
        skill_id=skill_id,
        path=skill_md,
        body=body.strip(),
        name=name,
        description=description,
    )


def read_skill_excerpt(skill_id: str, *, root: Path | None = None, max_chars: int = 2500) -> str:
    loaded = load_skill(skill_id, root=root)
    excerpt = loaded.body
    if len(excerpt) > max_chars:
        excerpt = excerpt[: max_chars - 1] + "…"
    return excerpt


def copy_rubric_skill_to_session(
    skill_id: str,
    session: WorkspaceSession,
    *,
    root: Path | None = None,
) -> Path:
    """Copy active rubric SKILL.md into workspace rubric/ for reviewer access."""
    loaded = load_skill(skill_id, root=root)
    target = session.rubric_dir / "active_skill.md"
    shutil.copy2(loaded.path, target)
    return target


def _assert_under_allowlist(path: Path, *, root: Path | None = None) -> None:
    resolved = path.resolve()
    roots = allowlist_roots(root=root)
    if not any(_is_relative_to(resolved, allowed) for allowed in roots):
        msg = f"Skill path outside allowlist: {resolved}"
        raise SkillLoadError(msg)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _parse_frontmatter(text: str, *, skill_id: str) -> tuple[str, str, str]:
    match = _FRONTMATTER.match(text.strip())
    if not match:
        return skill_id, skill_id, text
    meta_raw, body = match.group(1), match.group(2)
    name = skill_id
    description = ""
    for line in meta_raw.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip("\"'")
        elif line.startswith("description:"):
            description = line.split(":", 1)[1].strip().strip("\"'")
    if description.startswith(">"):
        # folded block scalar start — keep simple: use rest of meta until blank
        description = description.lstrip(">").strip()
    return name or skill_id, description or skill_id, body
