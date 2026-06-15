"""run_experiment dry-run, naming, and SSE context extraction tests."""

from __future__ import annotations

import json
from pathlib import Path

from app.agent.run_config import RunConfig
from dataset_registry import resolve_dataset_target, slug_to_run_suffix
from run_experiment import (
    AgentCallResult,
    build_run_metadata,
    extract_contexts_from_tool_result,
    merge_agent_call_results,
    parse_sse_event,
    resolve_eval_stream_url,
    run_name,
)

EVALS_ROOT = Path(__file__).resolve().parents[1]
CONFIG = EVALS_ROOT / "configs" / "baseline-react-inmemory.yaml"
MANIFEST = EVALS_ROOT / "datasets" / "e2e" / "e2e-qa" / "v001_2026-06-15.yaml"


def test_run_name_format() -> None:
    config = RunConfig.from_yaml_path(CONFIG)
    name = run_name(config, "e2e-qa")
    assert name.startswith("baseline-react-inmemory--e2e-qa--")
    parts = name.split("--")
    assert len(parts) == 4


def test_resolve_dataset_target() -> None:
    config = RunConfig.from_yaml_path(CONFIG)
    target = resolve_dataset_target(config, "e2e/e2e-qa")
    assert target.full_name == "e2e/e2e-qa/v001"
    assert target.version == "v001"
    assert target.manifest_path == MANIFEST


def test_run_metadata_contains_config_id() -> None:
    config = RunConfig.from_yaml_path(CONFIG)
    target = resolve_dataset_target(config, "e2e/e2e-qa")
    metadata = build_run_metadata(
        config,
        target=target,
        config_path=CONFIG,
    )
    assert metadata["config_id"] == "baseline-react-inmemory"
    assert metadata["dataset_slug"] == "e2e/e2e-qa"
    assert "judge_model" in metadata
    assert "evaluator_profile" in metadata


def test_resolve_eval_stream_url() -> None:
    assert resolve_eval_stream_url("http://localhost:8000/api/v1/chat").endswith("/chat/stream")
    assert resolve_eval_stream_url("http://localhost:8000/api/v1/chat/stream").endswith(
        "/chat/stream"
    )


def test_extract_contexts_from_search_tool() -> None:
    payload = json.dumps(
        [
            {"text": "chunk one", "source": "a.md"},
            {"text": "chunk two", "source": "b.md"},
        ],
        ensure_ascii=False,
    )
    contexts = extract_contexts_from_tool_result("search_knowledge_base_tool", payload)
    assert contexts == ["chunk one", "chunk two"]


def test_extract_contexts_ignores_other_tools() -> None:
    assert extract_contexts_from_tool_result("list_b2c_products", '[{"name": "x"}]') == []


def test_parse_sse_event_token_and_tool_result() -> None:
    token = parse_sse_event("token", {"text": "Hello "})
    tool = parse_sse_event(
        "tool_result",
        {
            "name": "search_knowledge_base_tool",
            "result": json.dumps([{"text": "KB hit"}]),
            "step_id": "2",
        },
    )
    assert token == AgentCallResult(answer="Hello ", contexts=[])
    assert tool == AgentCallResult(answer="", contexts=["KB hit"])


def test_parse_sse_event_tool_call() -> None:
    tool = parse_sse_event("tool_call", {"name": "create_payment_link", "args": {"product_id": "x"}})
    assert tool == AgentCallResult(tools_called=["create_payment_link"])


def test_merge_agent_call_results_tools() -> None:
    merged = merge_agent_call_results(
        [
            AgentCallResult(tools_called=["list_b2c_products"]),
            AgentCallResult(answer="Pay here", contexts=["KB"]),
            AgentCallResult(tools_called=["create_payment_link"]),
        ]
    )
    assert merged.tools_called == ["list_b2c_products", "create_payment_link"]
    assert merged.contexts == ["KB"]
