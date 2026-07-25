"""Single-agent homework review loop (S2)."""

from __future__ import annotations

import json
import logging
import time
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
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from homework_mentor.config import (
    DEFAULT_REVIEW_MODE,
    ReviewMode,
    ReviewPrompts,
    RuntimeSettings,
    apply_openrouter_process_env,
    init_openrouter_chat_model,
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
from homework_mentor.errors import describe_exception, is_transient_provider_error
from homework_mentor.logging_setup import setup_logging
from homework_mentor.orchestrator.agent import AgentError, extract_final_text
from homework_mentor.output.render import (
    FINAL_FEEDBACK_JSON,
    FIX_PLAN_JSON,
    load_final_feedback,
    load_fix_plan,
)
from homework_mentor.reviewers.collector import SubagentHandoffCollector
from homework_mentor.reviewers.registry import build_reviewer_subagents, load_reviewer_specs
from homework_mentor.reviewers.window_metrics import ReviewerWindowMetricsCollector
from homework_mentor.skills.activate import build_activate_review_skill_tool
from homework_mentor.workspace.events import WorkspaceEventCollector

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from langgraph.graph.state import CompiledStateGraph

    from homework_mentor.code_fetch.models import FetchResult
    from homework_mentor.output.schemas import FinalFeedback, FixPlan
    from homework_mentor.rubric.loader import RubricSelection
    from homework_mentor.skills.models import SkillRef, SkillsSelection
    from homework_mentor.submission.models import Submission
    from homework_mentor.synthesis.reflection import ReflectionResult
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
    subagent_handoffs: SubagentHandoffCollector = field(default_factory=SubagentHandoffCollector)
    final_feedback: FinalFeedback | None = None
    fix_plan: FixPlan | None = None
    reflection: ReflectionResult | None = None
    skills: SkillsSelection | None = None
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE


def _register_review_harness(model_name: str) -> None:
    register_harness_profile(
        model_name,
        HarnessProfile(
            excluded_tools=frozenset({"execute"}),
            excluded_middleware=frozenset({"SummarizationMiddleware"}),
            extra_middleware=pop_extra_middleware,
            general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
        ),
    )


def build_review_agent(  # noqa: PLR0913 — agent wiring needs explicit deps
    settings: RuntimeSettings,
    *,
    session_root: Path,
    skills_by_aspect: dict[str, list] | None = None,
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE,
    window_metrics: ReviewerWindowMetricsCollector | None = None,
    skills: SkillsSelection | None = None,
    session: WorkspaceSession | None = None,
) -> CompiledStateGraph[Any, Any, Any, Any]:
    """Build a Deep Agent scoped to one workspace session."""
    apply_openrouter_process_env(settings)
    model = init_openrouter_chat_model(settings)
    backend = FilesystemBackend(root_dir=session_root, virtual_mode=True)
    set_pending_summarization_middleware(
        build_summarization_middleware(model, backend, settings.yaml.agent.context),
    )
    _register_review_harness(settings.yaml.agent.model)
    permissions = [
        FilesystemPermission(
            operations=["read", "write", "list"],
            paths=["/**"],
            mode="allow",
        ),
    ]
    prompts = settings.yaml.review_prompts
    if review_mode == "subagents":
        reviewer_specs = load_reviewer_specs()
        reviewer_subagents = build_reviewer_subagents(
            reviewer_specs,
            model=model,
            skills_by_aspect=skills_by_aspect,
            window_metrics=window_metrics,
        )
        system_prompt = prompts.system_prompt
    else:
        reviewer_subagents = []
        system_prompt = prompts.single_system_prompt

    tools: list[Any] = []
    if skills is not None and session is not None:
        tools.append(
            build_activate_review_skill_tool(
                skills,
                session=session,
                skills_by_aspect=skills_by_aspect,
            ),
        )
        system_prompt = (
            f"{system_prompt.rstrip()}\n\n"
            "You may call activate_review_skill(skill_id, aspect, reason) to attach an "
            "on_demand skill (deep-agents-*, langchain-*, ecosystem-primer) when the "
            "submission clearly needs it. Prefer auto skills already listed; do not "
            "activate skills without a concrete reason. Activated excerpts land under "
            "/notes/skills/."
        )

    return create_deep_agent(
        model=model,
        backend=backend,
        permissions=permissions,
        system_prompt=system_prompt,
        subagents=reviewer_subagents,
        tools=tools,
        name="homework-mentor-review",
    )


def build_review_message(  # noqa: PLR0913 — explicit review message deps
    *,
    submission: Submission,
    fetch: FetchResult,
    rubric: RubricSelection,
    prompts: ReviewPrompts,
    skills: SkillsSelection | None = None,
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE,
) -> str:
    template = (
        prompts.review_user_template
        if review_mode == "subagents"
        else prompts.single_review_user_template
    )
    body = template.format(
        topic=submission.topic or "(not set)",
        source_type=submission.source_type.value,
        source=submission.source_value or "",
        file_count=fetch.file_count,
    )
    specs = load_reviewer_specs()
    reviewer_lines = "\n".join(
        f"- {spec.name}: aspect={spec.aspect}, criteria={', '.join(spec.criterion_ids)}"
        for spec in specs
    )
    if review_mode == "subagents":
        rubric_hint = f"rubric_id: {rubric.rubric.id}\nreviewers:\n{reviewer_lines}\n"
        stop_line = "Stop after reviewer summaries — synthesis writes final_feedback/fix_plan."
    else:
        rubric_hint = (
            f"rubric_id: {rubric.rubric.id}\naspects to cover in notes:\n{reviewer_lines}\n"
        )
        stop_line = "Stop after writing review notes — synthesis writes final_feedback/fix_plan."
    skills_hint = ""
    if skills is not None:
        skill_lines = "\n".join(
            f"- {ref.id} ({ref.kind}, source={ref.source}, "
            f"aspect={ref.aspect or 'all'}): {ref.reason}"
            for ref in skills.all_refs()
        )
        skills_hint = f"active_skills:\n{skill_lines}\n"
    return f"{body}\n{rubric_hint}{skills_hint}{stop_line}"


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


def load_final_artifacts_from_session(
    session: WorkspaceSession,
) -> tuple[FinalFeedback | None, FixPlan | None]:
    feedback_path = session.output_dir / FINAL_FEEDBACK_JSON
    plan_path = session.output_dir / FIX_PLAN_JSON
    feedback: FinalFeedback | None = None
    plan: FixPlan | None = None
    if feedback_path.is_file():
        try:
            feedback = load_final_feedback(feedback_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            logger.exception("failed to parse final_feedback.json")
    if plan_path.is_file():
        try:
            plan = load_fix_plan(plan_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            logger.exception("failed to parse fix_plan.json")
    return feedback, plan


@dataclass
class _ReviewStreamState:
    session: WorkspaceSession
    collector: WorkspaceEventCollector
    context_trace: ContextTraceCollector
    handoffs: SubagentHandoffCollector
    todo_history: list[list[TodoItem]]
    todos: list[TodoItem]
    observed_messages: int = 0


def _process_review_chunk(
    chunk: dict[str, Any],
    state: _ReviewStreamState,
) -> None:
    new_todos = _parse_todos(chunk.get("todos"))
    if new_todos and new_todos != state.todos:
        state.todos = new_todos
        state.todo_history.append(list(state.todos))
        _save_todo_snapshot(state.session, state.todos)
    messages = chunk.get("messages")
    ce_event = parse_summarization_state(chunk.get("_summarization_event"))
    if isinstance(messages, list):
        typed_messages = [item for item in messages if isinstance(item, BaseMessage)]
        new_messages = typed_messages[state.observed_messages :]
        state.observed_messages = len(typed_messages)
        if typed_messages:
            state.context_trace.observe_messages(
                typed_messages,
                event_type=ce_event.event_type if ce_event else "none",
                offload_path=ce_event.offload_path if ce_event else None,
            )
        for item in new_messages:
            state.handoffs.observe_message(item)
            _record_tool_events(state.collector, item)


def _stream_review_agent(
    agent: CompiledStateGraph[Any, Any, Any, Any],
    *,
    stream_input: dict[str, Any],
    state: _ReviewStreamState,
) -> dict[str, Any] | None:
    final_state: dict[str, Any] | None = None
    for chunk in agent.stream(stream_input, stream_mode="values"):
        if not isinstance(chunk, dict):
            continue
        final_state = chunk
        _process_review_chunk(chunk, state)
    return final_state


def run_review(  # noqa: PLR0913 — injectable deps for tests / skills wiring
    *,
    message: str,
    session: WorkspaceSession,
    settings: RuntimeSettings | None = None,
    agent_factory: Callable[[RuntimeSettings, Path], Any] | None = None,
    skills: SkillsSelection | None = None,
    skills_by_aspect: dict[str, list[SkillRef]] | None = None,
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE,
) -> ReviewRunResult:
    """Run the review agent with todo + FS event collection."""
    if not message.strip():
        msg = "review message must be non-empty"
        raise AgentError(msg)

    runtime = settings or load_runtime_settings()
    setup_logging(level=runtime.log_level)
    logger.info(
        "review start session=%s model=%s mode=%s",
        session.session_id,
        runtime.yaml.agent.model,
        review_mode,
    )

    aspect_skills = skills_by_aspect
    mode = review_mode
    skills_selection = skills
    review_session = session
    window_metrics = ReviewerWindowMetricsCollector()
    factory = agent_factory or (
        lambda s, root: build_review_agent(
            s,
            session_root=root,
            skills_by_aspect=aspect_skills,
            review_mode=mode,
            window_metrics=window_metrics,
            skills=skills_selection,
            session=review_session,
        )
    )
    agent = factory(runtime, session.root)
    collector = WorkspaceEventCollector()
    context_trace = ContextTraceCollector()
    handoffs = SubagentHandoffCollector()
    stream_state = _ReviewStreamState(
        session=session,
        collector=collector,
        context_trace=context_trace,
        handoffs=handoffs,
        todo_history=[],
        todos=[],
    )
    final_state: dict[str, Any] | None = None
    stream_input = {"messages": [{"role": "user", "content": message}]}
    attempts = 2

    for attempt in range(attempts):
        try:
            final_state = _stream_review_agent(
                agent,
                stream_input=stream_input,
                state=stream_state,
            )
            break
        except Exception as exc:
            transient = is_transient_provider_error(exc)
            if transient and attempt + 1 < attempts:
                logger.warning(
                    "review provider error (retry %s/%s) session=%s: %s",
                    attempt + 1,
                    attempts,
                    session.session_id,
                    describe_exception(exc),
                )
                time.sleep(2)
                continue
            logger.exception("review failed session=%s", session.session_id)
            msg = f"Review failed: {describe_exception(exc)}"
            raise AgentError(msg) from exc

    if final_state is None:
        msg = "Review agent produced no state"
        raise AgentError(msg)

    handoffs.merge_window_metrics(window_metrics)
    context_trace.persist(session)
    reply = extract_final_text(final_state)
    logger.info(
        "review done todos=%s context_steps=%s handoffs=%s",
        len(stream_state.todos),
        len(context_trace.events),
        len(handoffs.events),
    )
    return ReviewRunResult(
        reply=reply,
        todos=stream_state.todos,
        todo_history=stream_state.todo_history,
        events=collector,
        context_trace=context_trace,
        subagent_handoffs=handoffs,
        skills=skills,
        review_mode=review_mode,
    )
