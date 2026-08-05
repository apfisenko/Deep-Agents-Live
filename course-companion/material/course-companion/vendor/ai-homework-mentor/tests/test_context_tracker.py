from langchain_core.outputs import LLMResult

from mentor.agent.context_tracker import ContextTracker, TokenUsageCallback
from mentor.agent.reviewers import SubagentRun, enrich_subagent_runs
from mentor.agent.tools.rubric import _load_rubric
from mentor.agent.tools.skills_loader import build_skill_plan
from mentor.config import CONFIG_DIR


def test_parent_peak_excludes_subagent_metadata() -> None:
    tracker = ContextTracker()
    tracker.set_step("agent-review")
    callback = TokenUsageCallback(tracker)

    callback.on_llm_end(
        LLMResult(generations=[], llm_output={"token_usage": {"prompt_tokens": 5000}}),
        tags=[],
        metadata={"ls_agent_type": "subagent"},
    )
    assert tracker.parent_peak_tokens == 0
    assert len([s for s in tracker.steps if s.turn > 0]) == 0

    callback.on_llm_end(
        LLMResult(generations=[], llm_output={"token_usage": {"prompt_tokens": 4200}}),
        tags=[],
        metadata={"ls_agent_type": "root"},
    )
    assert tracker.parent_peak_tokens == 4200
    assert len([s for s in tracker.steps if s.turn > 0]) == 1


def test_parent_peak_excludes_task_tool_window() -> None:
    tracker = ContextTracker()
    tracker.set_step("agent-review")
    callback = TokenUsageCallback(tracker)

    callback.on_tool_start({"name": "task"}, '{"subagent_type": "reviewer-structure"}')
    callback.on_llm_end(
        LLMResult(generations=[], llm_output={"token_usage": {"prompt_tokens": 9000}}),
    )
    assert tracker.parent_peak_tokens == 0
    assert tracker.subagent_peak_tokens["reviewer-structure"] == 9000

    callback.on_tool_end("summary")
    callback.on_llm_end(
        LLMResult(generations=[], llm_output={"token_usage": {"prompt_tokens": 4800}}),
    )
    assert tracker.parent_peak_tokens == 4800


def test_skill_read_tracking_during_task() -> None:
    tracker = ContextTracker()
    callback = TokenUsageCallback(tracker)

    callback.on_tool_start(
        {"name": "task"},
        '{"subagent_type": "reviewer-api-design"}',
    )
    callback.on_tool_start(
        {"name": "read_file"},
        '{"path": "/skills/fastapi-templates/SKILL.md"}',
    )
    callback.on_tool_end("content")
    callback.on_tool_end("summary")

    confirmed = tracker.skills_confirmed_for("reviewer-api-design")
    assert confirmed == ("fastapi-templates",)


def test_enrich_subagent_runs_with_tracker() -> None:
    rubric = _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")
    plan = build_skill_plan(rubric)
    tracker = ContextTracker()
    tracker.record_skill_read("reviewer-api-design", "fastapi-templates")
    tracker.record_subagent_llm("reviewer-api-design", 3500, 200)

    runs = enrich_subagent_runs(
        [
            SubagentRun(
                name="reviewer-api-design",
                aspect_id="api-design",
                status="done",
                summary="ok",
            )
        ],
        plan,
        tracker,
    )
    assert runs[0].skills_applied == ("fastapi-templates",)
    assert runs[0].skills_confirmed == ("fastapi-templates",)
    assert runs[0].tokens == 3500
