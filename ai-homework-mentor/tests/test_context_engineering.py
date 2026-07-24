from __future__ import annotations

import yaml
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from homework_mentor.config import AgentConfig, ContextLimits, load_yaml_config
from homework_mentor.context.engineering import (
    build_summarization_middleware,
    parse_summarization_state,
)


def test_context_limits_defaults_from_yaml() -> None:
    cfg = load_yaml_config()
    ctx = cfg.agent.context
    assert ctx.window_tokens > 0
    assert ctx.summarize_enabled is True
    assert ctx.keep_messages == 20


def test_build_summarization_middleware_uses_yaml_threshold() -> None:
    model = GenericFakeChatModel(messages=iter([AIMessage(content="ok")]))
    context = ContextLimits(
        window_tokens=8000,
        summarize_threshold_tokens=128,
        offload_threshold_tokens=64,
        summarize_enabled=True,
        compact_enabled=True,
        keep_messages=5,
    )
    middleware = build_summarization_middleware(model, backend=None, context=context)
    assert middleware.trigger == ("tokens", 128)


def test_parse_summarization_offload_event() -> None:
    event = parse_summarization_state({"file_path": "/conversation_history/thread.md"})
    assert event is not None
    assert event.event_type == "offload"
    assert event.offload_path == "/conversation_history/thread.md"


def test_parse_summarization_summarize_event() -> None:
    event = parse_summarization_state({"cutoff_index": 3})
    assert event is not None
    assert event.event_type == "summarize"


def test_agent_yaml_context_threshold_not_hardcoded(tmp_path) -> None:
    config = tmp_path / "config"
    (config / "prompts").mkdir(parents=True)
    agent_data = {
        "model": "openrouter:test",
        "temperature": 0.1,
        "max_tokens": 100,
        "context": {
            "window_tokens": 4000,
            "summarize_threshold_tokens": 256,
            "offload_threshold_tokens": 128,
            "summarize_enabled": True,
            "compact_enabled": False,
            "keep_messages": 8,
        },
    }
    (config / "agent.yaml").write_text(yaml.dump(agent_data), encoding="utf-8")
    (config / "prompts" / "orchestrator.yaml").write_text("system_prompt: hi\n", encoding="utf-8")
    (config / "prompts" / "parse_submission.yaml").write_text(
        "system_prompt: parse\n",
        encoding="utf-8",
    )
    (config / "prompts" / "review.yaml").write_text(
        "system_prompt: review\nfeedback_json_schema: '{}'\nreview_user_template: '{topic}'\n",
        encoding="utf-8",
    )
    (config / "output.yaml").write_text("default_mode: compact\n", encoding="utf-8")
    parsed = load_yaml_config(root=tmp_path)
    assert parsed.agent.context.summarize_threshold_tokens == 256
    assert parsed.agent.context.keep_messages == 8
    assert AgentConfig.model_validate(agent_data).context.compact_enabled is False
