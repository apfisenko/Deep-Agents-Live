"""Stub orchestrator agent (DeepAgents + OpenRouter)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage

from homework_mentor.config import RuntimeSettings, load_runtime_settings
from homework_mentor.logging_setup import setup_logging

if TYPE_CHECKING:
    from collections.abc import Callable

    from langgraph.graph.state import CompiledStateGraph


class AgentError(RuntimeError):
    """Raised when the stub agent cannot produce a reply."""


def build_agent(settings: RuntimeSettings) -> CompiledStateGraph[Any, Any, Any, Any]:
    """Build a minimal DeepAgents graph from YAML settings."""
    agent_cfg = settings.yaml.agent
    model = init_chat_model(
        agent_cfg.model,
        api_key=settings.openrouter_api_key.get_secret_value(),
        temperature=agent_cfg.temperature,
        max_tokens=agent_cfg.max_tokens,
    )
    return create_deep_agent(
        model=model,
        tools=[],
        system_prompt=settings.yaml.orchestrator_prompts.system_prompt,
        name="homework-mentor-stub",
    )


def extract_final_text(result: dict[str, Any]) -> str:
    """Return the last AI message text from an agent invoke result."""
    messages = result.get("messages")
    if not isinstance(messages, list) or not messages:
        msg = "Agent result has no messages"
        raise AgentError(msg)

    for message in reversed(messages):
        if not _is_ai_message(message):
            continue
        text = _message_text(message)
        if text:
            return text

    msg = "Agent result has no AI text reply"
    raise AgentError(msg)


def run_agent(
    message: str,
    *,
    settings: RuntimeSettings | None = None,
    agent_factory: Callable[[RuntimeSettings], Any] | None = None,
) -> str:
    """Run one user message through the stub agent and return the reply text."""
    if not message.strip():
        msg = "message must be non-empty"
        raise AgentError(msg)

    runtime = settings or load_runtime_settings()
    logger = setup_logging(level=runtime.log_level)
    logger.info("session start model=%s", runtime.yaml.agent.model)

    # Ensure provider clients that read process env also see the key.
    os.environ["OPENROUTER_API_KEY"] = runtime.openrouter_api_key.get_secret_value()

    factory = agent_factory or build_agent
    agent = factory(runtime)
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    if not isinstance(result, dict):
        msg = f"Unexpected agent result type: {type(result)!r}"
        raise AgentError(msg)

    reply = extract_final_text(result)
    logger.info("session done reply_chars=%s", len(reply))
    return reply


def _is_ai_message(message: object) -> bool:
    if isinstance(message, AIMessage):
        return True
    if isinstance(message, BaseMessage):
        return message.type == "ai"
    if isinstance(message, dict):
        role = message.get("role") or message.get("type")
        return role in {"ai", "assistant"}
    return False


def _message_text(message: object) -> str:
    content: object
    if isinstance(message, BaseMessage):
        content = message.content
    elif isinstance(message, dict):
        content = message.get("content", "")
    else:
        return ""

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
