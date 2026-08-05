"""Context engineering visibility (S03+) and subagent tracking (S04+)."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

if TYPE_CHECKING:
    from mentor.agent.reviewers import SubagentRun

_SKILL_PATH_RE = re.compile(r"^/skills/([^/]+)")
_SKILL_TOOLS = frozenset({"read_file", "ls", "glob"})


@dataclass
class ContextStep:
    name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    event: str = ""
    turn: int = 0


@dataclass
class ContextTracker:
    steps: list[ContextStep] = field(default_factory=list)
    summarizations: int = 0
    offloads: int = 0
    parent_peak_tokens: int = 0
    subagent_runs: list[SubagentRun] = field(default_factory=list)
    subagent_peak_tokens: dict[str, int] = field(default_factory=dict)
    subagent_skill_reads: dict[str, set[str]] = field(default_factory=dict)
    _current_step: str = "init"
    _parent_turn: int = 0

    def set_step(self, name: str) -> None:
        self._current_step = name

    def record_llm_usage(self, prompt: int, completion: int) -> None:
        total = prompt + completion
        if self._current_step == "agent-review" and prompt:
            self.parent_peak_tokens = max(self.parent_peak_tokens, prompt)
        self._parent_turn += 1
        self.steps.append(
            ContextStep(
                name=self._current_step,
                prompt_tokens=prompt,
                completion_tokens=completion,
                total_tokens=total,
                turn=self._parent_turn,
            )
        )

    def record_subagent_llm(self, subagent_name: str, prompt: int, completion: int) -> None:
        if prompt:
            current = self.subagent_peak_tokens.get(subagent_name, 0)
            self.subagent_peak_tokens[subagent_name] = max(current, prompt)

    def record_skill_read(self, subagent_name: str, skill_name: str) -> None:
        reads = self.subagent_skill_reads.setdefault(subagent_name, set())
        reads.add(skill_name)

    def skills_confirmed_for(self, subagent_name: str) -> tuple[str, ...]:
        return tuple(sorted(self.subagent_skill_reads.get(subagent_name, set())))

    def tokens_for_subagent(self, subagent_name: str) -> int:
        return self.subagent_peak_tokens.get(subagent_name, 0)

    def record_summarization(self, before: int, after: int) -> None:
        self.summarizations += 1
        self.steps.append(
            ContextStep(
                name=self._current_step,
                total_tokens=after,
                event=f"SUMMARIZE {before}→{after}",
            )
        )

    def record_offload(self, path: str, saved_tokens: int) -> None:
        self.offloads += 1
        self.steps.append(
            ContextStep(
                name=self._current_step,
                event=f"OFFLOAD {path} (saved ~{saved_tokens} tok)",
            )
        )

    def record_subagent_runs(self, runs: list[SubagentRun]) -> None:
        self.subagent_runs = runs

    def total_tokens(self) -> int:
        return sum(s.total_tokens for s in self.steps)


def _parse_tool_input(input_str: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    inputs = kwargs.get("inputs")
    if isinstance(inputs, dict):
        return inputs
    if not input_str:
        return {}
    try:
        parsed = json.loads(input_str)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    try:
        parsed = ast.literal_eval(input_str)
        if isinstance(parsed, dict):
            return parsed
    except (SyntaxError, ValueError):
        pass
    return {}


def _skill_name_from_tool_input(tool_name: str, args: dict[str, Any]) -> str | None:
    if tool_name not in _SKILL_TOOLS:
        return None
    path = args.get("path") or args.get("file_path") or args.get("pattern") or ""
    if not isinstance(path, str):
        return None
    match = _SKILL_PATH_RE.match(path)
    if match:
        return match.group(1)
    if path.startswith("/skills/"):
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return parts[1]
    return None


class TokenUsageCallback(BaseCallbackHandler):
    def __init__(
        self,
        tracker: ContextTracker,
        *,
        progress: object | None = None,
    ) -> None:
        self.tracker = tracker
        self._progress = progress
        self._active_task_depth = 0
        self._subagent_stack: list[str] = []
        self._tool_stack: list[str] = []

    @staticmethod
    def _is_subagent_call(*, tags: list[str] | None, kwargs: dict[str, Any]) -> bool:
        metadata = kwargs.get("metadata")
        if isinstance(metadata, dict) and metadata.get("ls_agent_type") == "subagent":
            return True
        if tags:
            return any("subagent" in tag.lower() for tag in tags)
        return False

    @staticmethod
    def _subagent_name_from_metadata(kwargs: dict[str, Any]) -> str | None:
        metadata = kwargs.get("metadata")
        if isinstance(metadata, dict):
            name = metadata.get("lc_agent_name")
            if isinstance(name, str) and name:
                return name
        return None

    def _notify_tool(self, tool_name: str, detail: str = "") -> None:
        if self._progress is not None and hasattr(self._progress, "tool"):
            self._progress.tool(tool_name, detail)

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        tool_name = str(serialized.get("name", ""))
        self._tool_stack.append(tool_name)
        args = _parse_tool_input(input_str, kwargs)

        if tool_name == "task":
            self._active_task_depth += 1
            subagent_type = str(args.get("subagent_type", ""))
            if subagent_type:
                self._subagent_stack.append(subagent_type)
                self._notify_tool("task", subagent_type)
            return

        skill_name = _skill_name_from_tool_input(tool_name, args)
        if skill_name and self._subagent_stack:
            self.tracker.record_skill_read(self._subagent_stack[-1], skill_name)
            path = args.get("path") or args.get("file_path") or args.get("pattern") or ""
            self._notify_tool(tool_name, f"{path}")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        tool_name = self._tool_stack.pop() if self._tool_stack else ""
        if tool_name == "task" and self._active_task_depth > 0:
            self._active_task_depth -= 1
            if self._subagent_stack:
                self._subagent_stack.pop()

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        usage: dict[str, int] = {}
        if response.llm_output:
            usage = response.llm_output.get("token_usage") or {}
        prompt = int(usage.get("prompt_tokens", 0) or 0)
        completion = int(usage.get("completion_tokens", 0) or 0)
        if not prompt and not completion:
            return

        if self._active_task_depth > 0 and self._subagent_stack:
            self.tracker.record_subagent_llm(self._subagent_stack[-1], prompt, completion)
            return

        if self._is_subagent_call(tags=tags, kwargs=kwargs):
            subagent_name = self._subagent_name_from_metadata(kwargs)
            if subagent_name:
                self.tracker.record_subagent_llm(subagent_name, prompt, completion)
            return

        self.tracker.record_llm_usage(prompt, completion)
