from __future__ import annotations

import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import SecretStr

from homework_mentor.config import RuntimeSettings, load_yaml_config
from homework_mentor.context.tokens import measure_context_tokens
from homework_mentor.orchestrator.review import ReviewRunResult, run_review
from homework_mentor.reviewers.schemas import ReviewSummary
from homework_mentor.workspace import create_session


def test_run_review_collects_subagent_handoffs(tmp_path) -> None:
    session = create_session(root=tmp_path, session_id="subagents")
    runtime = RuntimeSettings(
        yaml=load_yaml_config(),
        openrouter_api_key=SecretStr("test-key"),
    )

    arch_summary = ReviewSummary(
        aspect="architecture",
        findings=["Module layout is clear"],
        criterion_ids=["packaging"],
        note_path="/notes/review_architecture.md",
    )
    quality_summary = ReviewSummary(
        aspect="code_quality",
        findings=["Improve error messages"],
        criterion_ids=["quality"],
        note_path="/notes/review_code_quality.md",
    )

    class FakeAgent:
        def stream(self, _input, *, stream_mode: str):
            yield {
                "messages": [
                    HumanMessage(content="user"),
                    AIMessage(
                        content="delegating",
                        tool_calls=[
                            {
                                "id": "t1",
                                "name": "task",
                                "args": {
                                    "subagent_type": "reviewer_architecture",
                                    "description": "Brief: check /code layout",
                                },
                            },
                        ],
                    ),
                    ToolMessage(
                        content=json.dumps(arch_summary.model_dump()),
                        name="task",
                        tool_call_id="t1",
                    ),
                    AIMessage(
                        content="delegating quality",
                        tool_calls=[
                            {
                                "id": "t2",
                                "name": "task",
                                "args": {
                                    "subagent_type": "reviewer_code_quality",
                                    "description": "Brief: scan /code for style",
                                },
                            },
                        ],
                    ),
                    ToolMessage(
                        content=json.dumps(quality_summary.model_dump()),
                        name="task",
                        tool_call_id="t2",
                    ),
                    AIMessage(content="done"),
                ],
                "todos": [],
            }

    def agent_factory(_settings, _root):
        return FakeAgent()

    result = run_review(
        message="check homework",
        session=session,
        settings=runtime,
        agent_factory=agent_factory,
    )
    assert isinstance(result, ReviewRunResult)
    assert len(result.subagent_handoffs.events) == 2
    aspects = result.subagent_handoffs.delegated_aspects()
    assert aspects == ["architecture", "code_quality"]
    for event in result.subagent_handoffs.events:
        assert event.summary
        assert event.summary_chars < 500


def test_parent_context_stays_below_s3_profile() -> None:
    """Documented S3 max ~980 tokens vs S4 parent with short summaries only."""
    s3_max_parent = 980
    s4_parent_messages = [
        HumanMessage(content="review via subagents"),
        AIMessage(content="delegating"),
        ToolMessage(content='{"findings":["ok"]}', name="task", tool_call_id="1"),
        ToolMessage(content='{"findings":["fix tests"]}', name="task", tool_call_id="2"),
        AIMessage(content="aggregated feedback ready"),
    ]
    tokens, _ = measure_context_tokens(s4_parent_messages)
    assert tokens < s3_max_parent
