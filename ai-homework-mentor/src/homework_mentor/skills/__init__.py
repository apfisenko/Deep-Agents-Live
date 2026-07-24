"""Skills layer: rubric + ecosystem routing for reviewers."""

from homework_mentor.skills.loader import (
    LoadedSkill,
    SkillLoadError,
    assert_skill_path_allowed,
    copy_rubric_skill_to_session,
    load_skill,
    read_skill_excerpt,
    resolve_skill_dir,
)
from homework_mentor.skills.models import SkillRef, SkillsSelection
from homework_mentor.skills.router import (
    SkillsRoutingError,
    detect_api,
    load_skills_routing,
    resolve_skills,
    resolve_skills_for_aspect,
)

__all__ = [
    "LoadedSkill",
    "SkillLoadError",
    "SkillRef",
    "SkillsRoutingError",
    "SkillsSelection",
    "assert_skill_path_allowed",
    "copy_rubric_skill_to_session",
    "detect_api",
    "load_skill",
    "load_skills_routing",
    "read_skill_excerpt",
    "resolve_skill_dir",
    "resolve_skills",
    "resolve_skills_for_aspect",
]
