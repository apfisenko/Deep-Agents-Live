"""Orchestrator — DeepAgents review session."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.summarization import SummarizationMiddleware
from deepagents.profiles.harness.harness_profiles import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    register_harness_profile,
)
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from mentor.agent.context_tracker import ContextTracker, TokenUsageCallback
from mentor.agent.reviewers import (
    SubagentRun,
    build_delegation_user_message,
    build_reviewer_subagents,
    enrich_subagent_runs,
    parse_task_messages,
)
from mentor.agent.synthesis import SynthesisResult, synthesize_review
from mentor.agent.tools.parse import (
    ParsedSubmission,
    SourceType,
    acquire_code,
    build_code_index,
    parse_submission,
)
from mentor.agent.tools.rubric import Rubric, select_rubric
from mentor.agent.tools.skills_loader import SkillPlan, materialize_workspace_skills
from mentor.agent.tools.workspace import Workspace, WorkspaceManager
from mentor.config import AppConfig, get_config

logger = logging.getLogger("mentor.agent")

_HARNESS_REGISTERED = False

MENTOR_HARNESS_PROFILE = HarnessProfile(
    general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
    excluded_middleware=frozenset({"SummarizationMiddleware"}),
)


def _ensure_harness_profile() -> None:
    global _HARNESS_REGISTERED  # noqa: PLW0603
    if _HARNESS_REGISTERED:
        return
    register_harness_profile("openai", MENTOR_HARNESS_PROFILE)
    _HARNESS_REGISTERED = True


def mentor_harness_profile() -> HarnessProfile:
    _ensure_harness_profile()
    return MENTOR_HARNESS_PROFILE


@dataclass
class RunResult:
    mode: str
    response: str
    workspace: Workspace | None
    rubric: Rubric | None
    file_count: int
    elapsed_s: float
    model: str
    config_path: str
    tracker: ContextTracker
    parsed: ParsedSubmission
    subagent_runs: list[SubagentRun]
    skill_plan: SkillPlan | None = None
    delegation_warning: str | None = None
    synthesis: SynthesisResult | None = None


class MentorOrchestrator:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config()
        self.workspace_manager = WorkspaceManager(self.config)
        _ensure_harness_profile()

    def _build_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.config.settings.openai_model,
            api_key=self.config.settings.openai_api_key,
            base_url=self.config.settings.openai_base_url,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            profile={"max_input_tokens": self.config.max_context_tokens},
        )

    def run(
        self,
        raw_input: str,
        *,
        topic: str | None = None,
        enable_review: bool = True,
        progress: object | None = None,
    ) -> RunResult:
        tracker = ContextTracker()
        started = time.perf_counter()
        if progress is not None and hasattr(progress, "phase"):
            progress.phase("parse")
        parsed = parse_submission(raw_input, topic_override=topic)

        if parsed.needs_topic and enable_review and parsed.source_type != SourceType.TEXT_ONLY:
            msg = (
                "Could not determine assignment topic. "
                'Re-run with --topic "Python Telegram bot" (or similar).'
            )
            raise ValueError(msg)

        model = self._build_model()

        if parsed.source_type == SourceType.TEXT_ONLY and not enable_review:
            if progress is not None and hasattr(progress, "phase"):
                progress.phase("chat")
            tracker.set_step("chat")
            result = model.invoke([HumanMessage(content=parsed.raw_input)])
            content = result.content if isinstance(result.content, str) else str(result.content)
            return RunResult(
                mode="chat",
                response=content,
                workspace=None,
                rubric=None,
                file_count=0,
                elapsed_s=time.perf_counter() - started,
                model=self.config.settings.openai_model,
                config_path=str(self.config.config_dir / "settings.yaml"),
                tracker=tracker,
                parsed=parsed,
                subagent_runs=[],
            )

        if parsed.source_type == SourceType.TEXT_ONLY:
            if progress is not None and hasattr(progress, "phase"):
                progress.phase("chat")
            tracker.set_step("chat")
            result = model.invoke([HumanMessage(content=parsed.raw_input)])
            content = result.content if isinstance(result.content, str) else str(result.content)
            return RunResult(
                mode="chat",
                response=content,
                workspace=None,
                rubric=None,
                file_count=0,
                elapsed_s=time.perf_counter() - started,
                model=self.config.settings.openai_model,
                config_path=str(self.config.config_dir / "settings.yaml"),
                tracker=tracker,
                parsed=parsed,
                subagent_runs=[],
            )

        seed = f"{parsed.source}:{parsed.topic}"
        workspace = self.workspace_manager.create(seed)
        if progress is not None and hasattr(progress, "phase"):
            progress.phase("acquire-code")
        tracker.set_step("acquire-code")
        file_count, source_kind = acquire_code(parsed, workspace.code_dir)
        code_index = build_code_index(workspace.code_dir)
        workspace.write_text(workspace.code_index_path, code_index)
        tracker.record_offload("/code-index.md", max(len(code_index) // 4, 1))

        if progress is not None and hasattr(progress, "phase"):
            progress.phase("select-rubric")
        rubric = select_rubric(self.config, parsed.topic)
        if progress is not None and hasattr(progress, "phase"):
            progress.phase("materialize-skills")
        skill_plan = materialize_workspace_skills(workspace, rubric)
        workspace.write_text(workspace.rubric_path, rubric.to_markdown())
        workspace.write_text(
            workspace.submission_path,
            f"# Submission\n\n- Source: {parsed.source}\n- Type: {source_kind}\n"
            f"- Topic: {parsed.topic}\n\n```\n{parsed.raw_input}\n```\n",
        )
        workspace.write_text(
            workspace.plan_path,
            "# Review plan\n\n"
            + "\n".join(
                f"- [ ] {a.get('id', 'aspect')}: {a.get('title', '')}" for a in rubric.aspects
            )
            + "\n",
        )

        system_prompt = self.config.load_prompt("orchestrator")
        reviewer_prompt = self.config.load_prompt("reviewer")
        subagents = build_reviewer_subagents(rubric, reviewer_prompt, skill_plan)
        backend = FilesystemBackend(root_dir=str(workspace.root), virtual_mode=True)

        summ = SummarizationMiddleware(
            model=model,
            backend=backend,
            trigger=("fraction", self.config.summarization_trigger_fraction),
            keep=("fraction", 0.15),
        )

        agent = create_deep_agent(
            model=model,
            system_prompt=system_prompt,
            backend=backend,
            middleware=[summ],
            subagents=subagents,
        )

        user_message = build_delegation_user_message(
            topic=parsed.topic or "",
            file_count=file_count,
            rubric=rubric,
        )

        if progress is not None and hasattr(progress, "phase"):
            progress.phase("agent-review")
        tracker.set_step("agent-review")
        callback = TokenUsageCallback(tracker, progress=progress)
        invoke_config: dict[str, Any] = {
            "configurable": {"thread_id": workspace.root.name},
            "callbacks": [callback],
        }

        state = agent.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=invoke_config,
        )

        messages = state.get("messages", [])
        if progress is not None and hasattr(progress, "phase"):
            progress.phase("synthesize")
        subagent_runs = enrich_subagent_runs(
            parse_task_messages(messages),
            skill_plan,
            tracker,
        )
        tracker.record_subagent_runs(subagent_runs)

        delegation_warning: str | None = None
        expected = len(rubric.aspects)
        if len(subagent_runs) < expected:
            delegation_warning = (
                f"Only {len(subagent_runs)}/{expected} aspects delegated via task. "
                "Check orchestrator prompt compliance."
            )
            logger.warning(delegation_warning)

        last_ai = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                last_ai = msg.content if isinstance(msg.content, str) else str(msg.content)
                break

        feedback = ""
        if workspace.feedback_path.exists():
            feedback = workspace.feedback_path.read_text(encoding="utf-8")
        elif last_ai:
            feedback = last_ai

        synthesis_result = synthesize_review(
            workspace,
            rubric,
            skill_plan=skill_plan,
            subagent_runs=subagent_runs,
            model=model,
            config=self.config,
            fallback_feedback=feedback,
        )
        feedback = workspace.feedback_path.read_text(encoding="utf-8")

        history = workspace.root / "conversation_history"
        if history.exists():
            tracker.record_summarization(
                before=tracker.total_tokens() or 1000,
                after=max(tracker.total_tokens() // 2, 100),
            )

        return RunResult(
            mode="review",
            response=feedback,
            workspace=workspace,
            rubric=rubric,
            file_count=file_count,
            elapsed_s=time.perf_counter() - started,
            model=self.config.settings.openai_model,
            config_path=str(self.config.config_dir / "settings.yaml"),
            tracker=tracker,
            parsed=parsed,
            subagent_runs=subagent_runs,
            skill_plan=skill_plan,
            delegation_warning=delegation_warning,
            synthesis=synthesis_result,
        )
