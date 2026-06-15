"""ReAct agent runner with optional SSE streaming."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from app.agent.config_registry import get_default_config_id, get_run_config
from app.agent.prompt_resolver import resolve_prompt
from app.agent.step_labels import (
    DEFAULT_ANALYZE_LABEL,
    DEFAULT_RESPOND_LABEL,
    label_for_tool,
)
from app.config import get_settings
from app.exceptions import AgentCoreError
from app.integrations.langfuse import get_langfuse_callbacks
from app.integrations.openrouter import create_chat_model, map_openai_exception
from app.memory.sessions import get_session_store
from app.tools.registry import get_agent_tools

if TYPE_CHECKING:
    from app.agent.run_config import RunConfig

logger = logging.getLogger(__name__)


@dataclass
class AgentRunResult:
    reply: str
    session_id: str


@dataclass
class StreamEvent:
    event: str
    data: dict[str, Any]


@dataclass
class _StreamState:
    step_counter: int = 0
    active_step_id: str | None = None
    reply_parts: list[str] = field(default_factory=list)

    def next_step_id(self) -> str:
        self.step_counter += 1
        return str(self.step_counter)


class ReactAgentRunner:
    def __init__(self, run_config: RunConfig) -> None:
        settings = get_settings()
        self._settings = settings
        self._run_config = run_config
        self._tools = get_agent_tools()
        self._graph = create_react_agent(
            create_chat_model(
                settings,
                model=run_config.model.name,
                temperature=run_config.model.temperature,
            ),
            self._tools,
            prompt=resolve_prompt(run_config.prompt),
        )

    @property
    def config_id(self) -> str:
        return self._run_config.config_id

    async def run(
        self,
        session_id: str,
        message: str,
        *,
        channel: str = "web",
        extra_metadata: dict[str, Any] | None = None,
    ) -> AgentRunResult:
        events: list[StreamEvent] = []
        async for event in self.stream(
            session_id,
            message,
            channel=channel,
            extra_metadata=extra_metadata,
        ):
            if event.event == "token":
                events.append(event)
        reply = "".join(item.data.get("text", "") for item in events if item.event == "token")
        if not reply:
            reply = "Извините, не удалось сформировать ответ."
        return AgentRunResult(reply=reply, session_id=session_id)

    async def stream(
        self,
        session_id: str,
        message: str,
        *,
        channel: str = "web",
        extra_metadata: dict[str, Any] | None = None,
    ) -> AsyncIterator[StreamEvent]:
        store = get_session_store()
        history = store.get_messages(session_id)
        state = _StreamState()

        yield StreamEvent(
            event="agent_step",
            data={"id": state.next_step_id(), "label": DEFAULT_ANALYZE_LABEL, "status": "active"},
        )
        analyze_id = str(state.step_counter)
        state.active_step_id = analyze_id

        messages = [*history, HumanMessage(content=message)]
        trace_metadata = {
            "channel": channel,
            "session_id": session_id,
            **self._run_config.to_metadata(),
        }
        if extra_metadata:
            trace_metadata.update(extra_metadata)
        config = cast(
            "RunnableConfig",
            {
                "callbacks": get_langfuse_callbacks(self._settings),
                "metadata": trace_metadata,
                "tags": [channel, self._run_config.config_id],
            },
        )

        try:
            async for graph_event in self._graph.astream_events(
                cast("Any", {"messages": messages}),
                config=config,
                version="v2",
            ):
                event_payload = cast("dict[str, Any]", graph_event)
                async for mapped in self._map_graph_event(event_payload, state):
                    yield mapped
        except AgentCoreError:
            raise
        except Exception as exc:
            raise map_openai_exception(exc) from exc

        yield StreamEvent(
            event="agent_step",
            data={"id": analyze_id, "label": DEFAULT_ANALYZE_LABEL, "status": "done"},
        )

        reply = "".join(state.reply_parts).strip() or "Извините, не удалось сформировать ответ."
        store.append_exchange(session_id, message, reply)
        yield StreamEvent(event="done", data={"session_id": session_id})

    async def _map_graph_event(
        self,
        graph_event: dict[str, Any],
        state: _StreamState,
    ) -> AsyncIterator[StreamEvent]:
        event_type = graph_event.get("event")
        name = graph_event.get("name", "")

        if event_type == "on_tool_start":
            step_id = state.next_step_id()
            state.active_step_id = step_id
            tool_input = graph_event.get("data", {}).get("input", {})
            yield StreamEvent(
                event="agent_step",
                data={"id": step_id, "label": label_for_tool(name), "status": "active"},
            )
            yield StreamEvent(
                event="tool_call",
                data={"name": name, "args": tool_input, "step_id": step_id},
            )
            return

        if event_type == "on_tool_end":
            step_id = state.active_step_id or state.next_step_id()
            output = graph_event.get("data", {}).get("output")
            result_payload: Any
            if hasattr(output, "content"):
                result_payload = output.content
            else:
                result_payload = output
            yield StreamEvent(
                event="tool_result",
                data={"name": name, "result": result_payload, "step_id": step_id},
            )
            yield StreamEvent(
                event="agent_step",
                data={"id": step_id, "label": label_for_tool(name), "status": "done"},
            )
            return

        if event_type == "on_chat_model_stream":
            chunk = graph_event.get("data", {}).get("chunk")
            text = _extract_chunk_text(chunk)
            if text:
                state.reply_parts.append(text)
                yield StreamEvent(event="token", data={"text": text})
            return

        if event_type == "on_chat_model_end" and not state.reply_parts:
            output = graph_event.get("data", {}).get("output")
            text = _extract_message_text(output)
            if text:
                state.reply_parts.append(text)
                respond_id = state.next_step_id()
                yield StreamEvent(
                    event="agent_step",
                    data={"id": respond_id, "label": DEFAULT_RESPOND_LABEL, "status": "done"},
                )
                yield StreamEvent(event="token", data={"text": text})


_runners: dict[str, ReactAgentRunner] = {}


def get_agent_runner(config_id: str | None = None) -> ReactAgentRunner:
    cid = config_id or get_default_config_id()
    if cid not in _runners:
        _runners[cid] = ReactAgentRunner(get_run_config(cid))
    return _runners[cid]


def reset_agent_runner() -> None:
    _runners.clear()


def format_sse(event: StreamEvent) -> str:
    return f"event: {event.event}\ndata: {json.dumps(event.data, ensure_ascii=False)}\n\n"


def _extract_chunk_text(chunk: Any) -> str:
    if chunk is None:
        return ""
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "".join(parts)
    return str(content)


def _extract_message_text(message: Any) -> str:
    if message is None:
        return ""
    if hasattr(message, "content"):
        content = message.content
        if isinstance(content, str):
            return content
    return ""
