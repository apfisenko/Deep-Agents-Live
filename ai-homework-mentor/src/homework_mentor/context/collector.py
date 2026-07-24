"""Collect and persist context metric events for a review session."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homework_mentor.context.models import ContextEventType, ContextMetricEvent
from homework_mentor.context.tokens import measure_context_tokens

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

    from homework_mentor.workspace.session import WorkspaceSession

_TRACE_RELATIVE = "notes/context_trace.jsonl"
_DEFAULT_RING_SIZE = 500


@dataclass
class ContextTraceCollector:
    """Ring-buffer of context metric events for one review run."""

    events: list[ContextMetricEvent] = field(default_factory=list)
    ring_size: int = _DEFAULT_RING_SIZE
    _step: int = 0
    _last_tokens: int = 0

    def observe_messages(
        self,
        messages: list[BaseMessage],
        *,
        event_type: ContextEventType = "none",
        offload_path: str | None = None,
    ) -> ContextMetricEvent | None:
        """Record a step when message history size changes."""
        tokens_after, source = measure_context_tokens(messages)
        if self._step > 0 and tokens_after == self._last_tokens and event_type == "none":
            return None

        event = ContextMetricEvent(
            step=self._step,
            tokens_before=self._last_tokens,
            tokens_after=tokens_after,
            source=source,
            event_type=event_type,
            offload_path=offload_path,
        )
        self.events.append(event)
        if len(self.events) > self.ring_size:
            self.events = self.events[-self.ring_size :]
        self._step += 1
        self._last_tokens = tokens_after
        return event

    def persist(self, session: WorkspaceSession) -> str:
        """Write trace to workspace notes; return relative path."""
        lines = [event.model_dump_json() for event in self.events]
        content = "\n".join(lines) + ("\n" if lines else "")
        session.write_text(_TRACE_RELATIVE, content)
        return _TRACE_RELATIVE

    @classmethod
    def load_from_session(cls, session: WorkspaceSession) -> list[ContextMetricEvent]:
        path = session.notes_dir / "context_trace.jsonl"
        if not path.is_file():
            return []
        events: list[ContextMetricEvent] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            events.append(ContextMetricEvent.model_validate(json.loads(line)))
        return events
