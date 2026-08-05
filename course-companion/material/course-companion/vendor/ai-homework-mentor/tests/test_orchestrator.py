from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from mentor.agent.orchestrator import mentor_harness_profile
from mentor.agent.reviewers import (
    build_reviewer_subagents,
    parse_task_messages,
    reviewer_name,
)
from mentor.agent.tools.rubric import _load_rubric
from mentor.agent.tools.skills_loader import build_skill_plan
from mentor.config import CONFIG_DIR, get_config


def test_build_reviewer_subagents_count() -> None:
    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")
    config = get_config()
    prompt = config.load_prompt("reviewer")
    plan = build_skill_plan(rubric)
    subagents = build_reviewer_subagents(rubric, prompt, plan)
    assert len(subagents) >= 3


def test_build_reviewer_subagents_names() -> None:
    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")
    config = get_config()
    prompt = config.load_prompt("reviewer")
    plan = build_skill_plan(rubric)
    subagents = build_reviewer_subagents(rubric, prompt, plan)
    for aspect in rubric.aspects:
        aspect_id = str(aspect.get("id"))
        expected = reviewer_name(aspect_id)
        names = [s["name"] for s in subagents]
        assert expected in names


def test_build_reviewer_subagents_has_skills() -> None:
    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")
    config = get_config()
    prompt = config.load_prompt("reviewer")
    plan = build_skill_plan(rubric)
    subagents = build_reviewer_subagents(rubric, prompt, plan)
    api_design = next(s for s in subagents if s["name"] == "reviewer-api-design")
    assert "/skills/fastapi-templates" in api_design["skills"]


def test_parse_task_messages() -> None:
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call-1",
                    "name": "task",
                    "args": {
                        "subagent_type": "reviewer-structure",
                        "description": "Review structure. Brief at /notes/brief-structure.md",
                    },
                }
            ],
        ),
        ToolMessage(
            content="Good layout. Missing routers package split.",
            tool_call_id="call-1",
        ),
    ]
    runs = parse_task_messages(messages)
    assert len(runs) == 1
    assert runs[0].name == "reviewer-structure"
    assert runs[0].aspect_id == "structure"
    assert runs[0].status == "done"
    assert len(runs[0].summary) < 500
    assert runs[0].brief_path == "/notes/brief-structure.md"


def test_parse_task_messages_ignores_non_reviewers() -> None:
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call-2",
                    "name": "task",
                    "args": {
                        "subagent_type": "general-purpose",
                        "description": "do something",
                    },
                }
            ],
        ),
        ToolMessage(content="done", tool_call_id="call-2"),
        HumanMessage(content="ignored"),
    ]
    runs = parse_task_messages(messages)
    assert runs == []


def test_harness_allows_task() -> None:
    profile = mentor_harness_profile()
    assert "task" not in profile.excluded_tools
    assert profile.general_purpose_subagent.enabled is False
