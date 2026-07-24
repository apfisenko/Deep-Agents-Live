from __future__ import annotations

from pathlib import Path

from homework_mentor.reviewers.registry import (
    build_reviewer_subagents,
    criterion_owner_map,
    load_reviewer_specs,
)
from homework_mentor.reviewers.window_metrics import ReviewerWindowMetricsCollector
from homework_mentor.skills.models import SkillRef


def test_load_reviewer_specs_at_least_two() -> None:
    specs = load_reviewer_specs()
    assert len(specs) >= 2
    names = {spec.name for spec in specs}
    assert "reviewer_architecture" in names
    assert "reviewer_code_quality" in names


def test_criterion_owners_do_not_overlap_primary() -> None:
    specs = load_reviewer_specs()
    owners = criterion_owner_map(specs)
    assert owners["quality"] == "code_quality"
    assert owners["packaging"] == "architecture"


def test_build_reviewer_subagents_use_prompt_json_not_response_format() -> None:
    specs = load_reviewer_specs()
    subagents = build_reviewer_subagents(specs, model="openrouter:test")
    assert len(subagents) == len(specs)
    for spec, subagent in zip(specs, subagents, strict=True):
        assert subagent["name"] == spec.name
        assert subagent.get("response_format") is None
        assert subagent.get("middleware") is None
        assert "JSON object only" in subagent["system_prompt"]


def test_build_reviewer_subagents_attach_window_metrics_middleware() -> None:
    specs = load_reviewer_specs()
    metrics = ReviewerWindowMetricsCollector()
    subagents = build_reviewer_subagents(
        specs,
        model="openrouter:test",
        window_metrics=metrics,
    )
    for subagent in subagents:
        middleware = subagent.get("middleware")
        assert isinstance(middleware, list)
        assert len(middleware) == 1


def test_build_reviewer_subagents_include_skill_excerpt() -> None:
    specs = load_reviewer_specs()
    skills = {
        "code_quality": [
            SkillRef(
                id="modern-python",
                path=str(Path("x")),
                kind="ecosystem",
                reason="test",
                aspect="code_quality",
            ),
        ],
    }
    subagents = build_reviewer_subagents(specs, model="openrouter:test", skills_by_aspect=skills)
    quality = next(item for item in subagents if item["name"] == "reviewer_code_quality")
    assert "modern-python" in quality["system_prompt"]
    assert "--- begin modern-python ---" in quality["system_prompt"]
