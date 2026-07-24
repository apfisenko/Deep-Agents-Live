"""Collect subagent handoff events from orchestrator stream (S4)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from homework_mentor.reviewers.schemas import ReviewSummary, expected_note_path

if TYPE_CHECKING:
    from homework_mentor.reviewers.window_metrics import ReviewerWindowMetricsCollector


@dataclass
class SubagentHandoffEvent:
    """One reviewer delegation observed in the parent agent stream."""

    aspect: str
    subagent_name: str
    brief: str
    summary: str | None = None
    note_path: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = None
    max_window_tokens: int | None = None
    total_window_tokens_estimate: int | None = None
    model_calls: int | None = None
    window_metric_source: str | None = None

    @property
    def duration_ms(self) -> int | None:
        if self.completed_at is None:
            return None
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() * 1000)

    @property
    def brief_chars(self) -> int:
        return len(self.brief)

    @property
    def summary_chars(self) -> int:
        return len(self.summary or "")


class SubagentHandoffCollector:
    """Track task-tool delegations in the orchestrator message stream."""

    def __init__(self) -> None:
        self.events: list[SubagentHandoffEvent] = []
        self._pending: dict[str, SubagentHandoffEvent] = {}

    def merge_window_metrics(self, metrics: ReviewerWindowMetricsCollector) -> None:
        """Attach per-reviewer window token stats collected inside subagents."""
        for event in self.events:
            snap = metrics.get(event.subagent_name)
            if snap is None:
                # Fallback: match by aspect when names diverge slightly.
                snap = next(
                    (item for item in metrics.snapshots() if item.aspect == event.aspect),
                    None,
                )
            if snap is None:
                continue
            event.max_window_tokens = snap.max_tokens
            event.total_window_tokens_estimate = snap.total_tokens_estimate
            event.model_calls = snap.model_calls
            event.window_metric_source = snap.source

    def observe_message(self, message: BaseMessage) -> None:
        if isinstance(message, AIMessage) and message.tool_calls:
            self._observe_task_calls(message)
            return
        if isinstance(message, ToolMessage) and message.name == "task":
            self._observe_task_result(message)

    def delegated_aspects(self) -> list[str]:
        return [event.aspect for event in self.events]

    def _observe_task_calls(self, message: AIMessage) -> None:
        for call in message.tool_calls or []:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
            if name != "task":
                continue
            args = call.get("args") if isinstance(call, dict) else getattr(call, "args", {})
            if not isinstance(args, dict):
                continue
            subagent_type = args.get("subagent_type")
            description = args.get("description")
            if not isinstance(subagent_type, str) or not isinstance(description, str):
                continue
            call_id = call.get("id") if isinstance(call, dict) else getattr(call, "id", None)
            aspect = _aspect_from_subagent_name(subagent_type)
            event = SubagentHandoffEvent(
                aspect=aspect,
                subagent_name=subagent_type,
                brief=description.strip(),
                note_path=expected_note_path(aspect),
            )
            self.events.append(event)
            if isinstance(call_id, str):
                self._pending[call_id] = event

    def _observe_task_result(self, message: ToolMessage) -> None:
        content = _tool_content_text(message)
        call_id = message.tool_call_id
        event = self._pending.pop(call_id, None) if call_id else None
        if event is None and self.events:
            event = next((item for item in reversed(self.events) if item.summary is None), None)
        if event is None:
            return
        event.summary = content
        event.completed_at = datetime.now(tz=UTC)
        parsed_path = _extract_note_path(content)
        if parsed_path:
            event.note_path = parsed_path


def _aspect_from_subagent_name(name: str) -> str:
    prefix = "reviewer_"
    if name.startswith(prefix):
        return name[len(prefix) :]
    return name


def _tool_content_text(message: ToolMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts).strip()
    return str(content).strip()


def _extract_note_path(content: str) -> str | None:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    note_path = payload.get("note_path")
    if isinstance(note_path, str) and note_path.startswith("/notes/"):
        return note_path
    summary = payload.get("structured_response")
    if isinstance(summary, dict):
        path = summary.get("note_path")
        if isinstance(path, str):
            return path
    return None


def parse_review_summary(content: str) -> ReviewSummary | None:
    """Parse subagent handoff JSON from tool message or final assistant text."""
    for candidate in _json_candidates(content):
        payload = _load_json_dict(candidate)
        if payload is None:
            continue
        if "structured_response" in payload and isinstance(payload["structured_response"], dict):
            payload = payload["structured_response"]
        try:
            return ReviewSummary.model_validate(payload)
        except ValueError:
            continue
    return None


_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def _json_candidates(content: str) -> list[str]:
    text = content.strip()
    if not text:
        return []
    candidates = [text]
    candidates.extend(match.group(1).strip() for match in _JSON_FENCE.finditer(text))
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    return candidates


def _load_json_dict(raw: str) -> dict[str, object] | None:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None
