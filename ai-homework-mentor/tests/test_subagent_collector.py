from __future__ import annotations

import json

from langchain_core.messages import AIMessage, ToolMessage

from homework_mentor.reviewers.collector import SubagentHandoffCollector, parse_review_summary
from homework_mentor.reviewers.schemas import ReviewSummary


def test_collector_records_brief_and_summary() -> None:
    collector = SubagentHandoffCollector()
    collector.observe_message(
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call-1",
                    "name": "task",
                    "args": {
                        "subagent_type": "reviewer_architecture",
                        "description": "Review packaging for /code/main.py",
                    },
                },
            ],
        ),
    )
    summary_payload = ReviewSummary(
        aspect="architecture",
        findings=["Clear src layout"],
        criterion_ids=["packaging"],
        note_path="/notes/review_architecture.md",
    )
    collector.observe_message(
        ToolMessage(
            content=json.dumps(summary_payload.model_dump()),
            name="task",
            tool_call_id="call-1",
        ),
    )
    assert len(collector.events) == 1
    event = collector.events[0]
    assert event.aspect == "architecture"
    assert event.summary is not None
    assert event.note_path == "/notes/review_architecture.md"
    assert event.duration_ms is not None
    assert collector.delegated_aspects() == ["architecture"]


def test_parse_review_summary_from_json() -> None:
    payload = ReviewSummary(
        aspect="code_quality",
        findings=["Add error handling"],
        criterion_ids=["quality"],
    )
    parsed = parse_review_summary(json.dumps(payload.model_dump()))
    assert parsed is not None
    assert parsed.findings[0] == "Add error handling"


def test_parse_review_summary_from_json_fence() -> None:
    payload = (
        '{"aspect":"architecture","findings":["ok"],"criterion_ids":["packaging"],'
        '"risks":[],"open_questions":[],"note_path":"/notes/review_architecture.md"}'
    )
    wrapped = f"Here is the summary:\n```json\n{payload}\n```"
    parsed = parse_review_summary(wrapped)
    assert parsed is not None
    assert parsed.aspect == "architecture"
