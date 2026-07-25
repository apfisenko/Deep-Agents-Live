"""Skills layer: rubric + ecosystem routing for reviewers."""

from homework_mentor.skills.activate import (
    SkillActivateError,
    activate_skill,
    build_activate_review_skill_tool,
)
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
    detect_docker,
    detect_packaging,
    detect_tests,
    load_skills_routing,
    resolve_skills,
    resolve_skills_for_aspect,
)

__all__ = [
    "LoadedSkill",
    "SkillActivateError",
    "SkillLoadError",
    "SkillRef",
    "SkillsRoutingError",
    "SkillsSelection",
    "activate_skill",
    "assert_skill_path_allowed",
    "build_activate_review_skill_tool",
    "copy_rubric_skill_to_session",
    "detect_api",
    "detect_docker",
    "detect_packaging",
    "detect_tests",
    "load_skill",
    "load_skills_routing",
    "read_skill_excerpt",
    "resolve_skill_dir",
    "resolve_skills",
    "resolve_skills_for_aspect",
]
