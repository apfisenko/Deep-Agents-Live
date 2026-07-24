"""Single-agent homework review loop (S2)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from deepagents import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    create_deep_agent,
    register_harness_profile,
)
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemPermission
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from homework_mentor.config import (
    ReviewPrompts,
    RuntimeSettings,
    load_runtime_settings,
)
from homework_mentor.context.collector import ContextTraceCollector
from homework_mentor.context.engineering import (
    build_summarization_middleware,
    parse_summarization_state,
)
from homework_mentor.context.harness import (
    pop_extra_middleware,
    set_pending_summarization_middleware,
)
from homework_mentor.feedback.models import SimpleFeedback
from homework_mentor.logging_setup import setup_logging
from homework_mentor.orchestrator.agent import AgentError, extract_final_text
from homework_mentor.workspace.events import WorkspaceEventCollector

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from langgraph.graph.state import CompiledStateGraph

    from homework_mentor.code_fetch.models import FetchResult
    from homework_mentor.rubric.loader import RubricSelection
    from homework_mentor.submission.models import Submission
    from homework_mentor.workspace.session import WorkspaceSession

logger = logging.getLogger(__name__)

TodoStatus = Literal["pending", "in_progress", "completed"]


@dataclass(frozen=True)
class TodoItem:
    content: str
    status: TodoStatus


@dataclass
class ReviewRunResult:
    reply: str
    todos: list[TodoItem] = field(default_factory=list)
    todo_history: list[list[TodoItem]] = field(default_factory=list)
    events: WorkspaceEventCollector = field(default_factory=WorkspaceEventCollector)
    context_trace: ContextTraceCollector = field(default_factory=ContextTraceCollector)
    feedback: SimpleFeedback | None = None


def _register_review_harness(model_name: str) -> None:
    register_harness_profile(
        model_name,
        HarnessProfile(
            excluded_tools=frozenset({"execute", "task"}),
            excluded_middleware=frozenset({"SummarizationMiddleware"}),
            extra_middleware=pop_extra_middleware,
            general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
        ),
    )


def build_review_agent(
    settings: RuntimeSettings,
    *,
    session_root: Path,
) -> CompiledStateGraph[Any, Any, Any, Any]:
    """Build a Deep Agent scoped to one workspace session."""
    agent_cfg = settings.yaml.agent
    model = init_chat_model(
        agent_cfg.model,
        api_key=settings.openrouter_api_key.get_secret_value(),
        temperature=agent_cfg.temperature,
        max_tokens=agent_cfg.max_tokens,
    )
    backend = FilesystemBackend(root_dir=session_root, virtual_mode=True)
    set_pending_summarization_middleware(
        build_summarization_middleware(model, backend, agent_cfg.context),
    )
    _register_review_harness(agent_cfg.model)
    permissions = [
        FilesystemPermission(
            operations=["read", "write", "list"],
            paths=["/**"],
            mode="allow",
        ),
    ]
    system_prompt = settings.yaml.review_prompts.system_prompt
    return create_deep_agent(
        model=model,
        backend=backend,
        permissions=permissions,
        system_prompt=system_prompt,
        name="homework-mentor-review",
    )


def build_review_message(
    *,
    submission: Submission,
    fetch: FetchResult,
    rubric: RubricSelection,
    prompts: ReviewPrompts,
) -> str:
    template = prompts.review_user_template
    schema = prompts.feedback_json_schema.strip()
    body = template.format(
        topic=submission.topic or "(not set)",
        source_type=submission.source_type.value,
        source=submission.source_value or "",
        file_count=fetch.file_count,
    )
    rubric_hint = f"rubric_id: {rubric.rubric.id}\n"
    return f"{body}\n{rubric_hint}\nRequired /output/feedback.json schema:\n{schema}"


def _parse_todos(raw: object) -> list[TodoItem]:
    if not isinstance(raw, list):
        return []
    items: list[TodoItem] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        content = entry.get("content")
        status = entry.get("status")
        if isinstance(content, str) and status in {"pending", "in_progress", "completed"}:
            items.append(TodoItem(content=content, status=status))
    return items


def _record_tool_events(collector: WorkspaceEventCollector, message: BaseMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        for call in message.tool_calls:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
            args = call.get("args") if isinstance(call, dict) else getattr(call, "args", {})
            if not isinstance(args, dict):
                continue
            path = args.get("path") or args.get("file_path")
            if not isinstance(path, str):
                continue
            if name in {"read_file", "grep", "glob"}:
                collector.record_read(path)
            elif name in {"write_file", "edit_file"}:
                collector.record_write(path)
    if isinstance(message, ToolMessage):
        tool_name = message.name or ""
        if tool_name == "write_todos":
            collector.record_created("/plan/todos")


def _save_todo_snapshot(session: WorkspaceSession, todos: list[TodoItem]) -> None:
    payload = [{"content": item.content, "status": item.status} for item in todos]
    target = session.plan_dir / "todo.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_feedback_from_session(session: WorkspaceSession) -> SimpleFeedback | None:
    path = session.output_dir / "feedback.json"
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return SimpleFeedback.model_validate(raw)
    except (json.JSONDecodeError, ValueError):
        logger.exception("failed to parse feedback.json")
        return None


def run_review(
    *,
    message: str,
    session: WorkspaceSession,
    settings: RuntimeSettings | None = None,
    agent_factory: Callable[[RuntimeSettings, Path], Any] | None = None,
) -> ReviewRunResult:
    """Run the review agent with todo + FS event collection."""
    if not message.strip():
        msg = "review message must be non-empty"
        raise AgentError(msg)

    runtime = settings or load_runtime_settings()
    setup_logging(level=runtime.log_level)
    logger.info("review start session=%s model=%s", session.session_id, runtime.yaml.agent.model)

    factory = agent_factory or (lambda s, root: build_review_agent(s, session_root=root))
    agent = factory(runtime, session.root)
    collector = WorkspaceEventCollector()
    context_trace = ContextTraceCollector()
    todo_history: list[list[TodoItem]] = []
    todos: list[TodoItem] = []
    final_state: dict[str, Any] | None = None

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode="values",
    ):
        if not isinstance(chunk, dict):
            continue
        final_state = chunk
        new_todos = _parse_todos(chunk.get("todos"))
        if new_todos and new_todos != todos:
            todos = new_todos
            todo_history.append(list(todos))
            _save_todo_snapshot(session, todos)
        messages = chunk.get("messages")
        ce_event = parse_summarization_state(chunk.get("_summarization_event"))
        if isinstance(messages, list):
            typed_messages = [item for item in messages if isinstance(item, BaseMessage)]
            if typed_messages:
                context_trace.observe_messages(
                    typed_messages,
                    event_type=ce_event.event_type if ce_event else "none",
                    offload_path=ce_event.offload_path if ce_event else None,
                )
            for item in typed_messages:
                _record_tool_events(collector, item)

    if final_state is None:
        msg = "Review agent produced no state"
        raise AgentError(msg)

    context_trace.persist(session)
    reply = extract_final_text(final_state)
    feedback = load_feedback_from_session(session)
    logger.info(
        "review done todos=%s feedback=%s context_steps=%s",
        len(todos),
        feedback is not None,
        len(context_trace.events),
    )
    return ReviewRunResult(
        reply=reply,
        todos=todos,
        todo_history=todo_history,
        events=collector,
        context_trace=context_trace,
        feedback=feedback,
    )
