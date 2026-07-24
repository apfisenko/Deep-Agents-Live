from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage
from pydantic import SecretStr

from homework_mentor.config import RuntimeSettings, load_yaml_config
from homework_mentor.context.collector import ContextTraceCollector
from homework_mentor.context.tokens import measure_context_tokens
from homework_mentor.orchestrator.review import ReviewRunResult, run_review
from homework_mentor.workspace import create_session


def test_measure_context_tokens_estimate() -> None:
    messages = [HumanMessage(content="hello"), AIMessage(content="world")]
    tokens, source = measure_context_tokens(messages)
    assert tokens > 0
    assert source == "estimate"


def test_measure_context_tokens_model_usage() -> None:
    messages = [
        HumanMessage(content="hello"),
        AIMessage(
            content="world",
            usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        ),
    ]
    tokens, source = measure_context_tokens(messages)
    assert tokens > 0
    assert source == "model_usage"


def test_context_trace_collector_records_steps() -> None:
    collector = ContextTraceCollector()
    first = [HumanMessage(content="review this homework please")]
    event = collector.observe_messages(first)
    assert event is not None
    assert event.step == 0
    assert event.tokens_before == 0
    assert event.tokens_after > event.tokens_before

    second = [*first, AIMessage(content="I'll start by reading the rubric.")]
    event2 = collector.observe_messages(second)
    assert event2 is not None
    assert event2.step == 1
    assert event2.tokens_before == event.tokens_after


def test_context_trace_persist_and_load(tmp_path) -> None:
    session = create_session(root=tmp_path, session_id="ctx")
    collector = ContextTraceCollector()
    collector.observe_messages([HumanMessage(content="step one")])
    rel = collector.persist(session)
    assert rel == "notes/context_trace.jsonl"
    trace_path = session.notes_dir / "context_trace.jsonl"
    assert trace_path.is_file()
    loaded = ContextTraceCollector.load_from_session(session)
    assert len(loaded) == 1
    assert loaded[0].tokens_after > 0


def test_run_review_records_context_trace(tmp_path) -> None:
    session = create_session(root=tmp_path, session_id="review-ctx")
    runtime = RuntimeSettings(
        yaml=load_yaml_config(),
        openrouter_api_key=SecretStr("test-key"),
    )

    class FakeAgent:
        def stream(self, _input, *, stream_mode: str):
            yield {
                "messages": [HumanMessage(content="user"), AIMessage(content="assistant")],
                "todos": [],
                "_summarization_event": {"file_path": "/conversation_history/run.md"},
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
    assert len(result.context_trace.events) >= 1
    assert any(event.event_type == "offload" for event in result.context_trace.events)
    assert (session.notes_dir / "context_trace.jsonl").is_file()
