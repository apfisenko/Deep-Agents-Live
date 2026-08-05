"""Тесты A2A checker client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from course_companion.subagents.a2a_checker import (
    A2ACheckerClient,
    A2ACheckerError,
)


def _mock_client(*, get_side_effect=None, post_side_effect=None) -> MagicMock:
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    if get_side_effect is not None:
        client.get.side_effect = get_side_effect
    if post_side_effect is not None:
        client.post.side_effect = post_side_effect
    return client


def test_discover_caches_agent_card() -> None:
    card = {"name": "checker", "url": "http://localhost:2025/a2a/uuid"}
    client = A2ACheckerClient("http://localhost:2025")

    with patch("course_companion.subagents.a2a_checker.httpx.Client") as factory:
        factory.return_value = _mock_client(
            get_side_effect=[MagicMock(status_code=200, json=MagicMock(return_value=card))]
        )
        first = client.discover()
        second = client.discover()

    assert first == card
    assert second == card
    assert client.rpc_path == "/a2a/uuid"


def test_discover_falls_back_to_assistant_search() -> None:
    card = {"name": "checker", "url": "http://localhost:2025/a2a/abc"}
    assistants = [{"graph_id": "checker", "assistant_id": "abc"}]
    search_resp = MagicMock(status_code=200, json=MagicMock(return_value=assistants))
    card_resp = MagicMock(status_code=200, json=MagicMock(return_value=card))
    client = A2ACheckerClient("http://localhost:2025")

    with patch("course_companion.subagents.a2a_checker.httpx.Client") as factory:
        factory.return_value = _mock_client(
            get_side_effect=[MagicMock(status_code=404), card_resp],
            post_side_effect=[search_resp],
        )
        discovered = client.discover(force=True)

    assert discovered["url"] == card["url"]


def test_send_message_jsonrpc() -> None:
    task = {"id": "ctx:run", "contextId": "ctx", "status": {"state": "working"}}
    rpc_resp = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"jsonrpc": "2.0", "id": "1", "result": task}),
    )
    client = A2ACheckerClient("http://localhost:2025")
    client._rpc_url = "http://localhost:2025/a2a/uuid"  # noqa: SLF001

    with patch("course_companion.subagents.a2a_checker.httpx.Client") as factory:
        factory.return_value = _mock_client(post_side_effect=[rpc_resp])
        result = client.send_message("submission: ./hw\ntopic: python-cli")

    assert result["id"] == "ctx:run"
    payload = factory.return_value.post.call_args.kwargs["json"]
    assert payload["method"] == "message/send"
    assert payload["params"]["message"]["parts"][0]["text"].startswith("submission:")


def test_get_task_and_map_status() -> None:
    completed = {
        "id": "t1",
        "status": {"state": "completed"},
        "artifacts": [{"parts": [{"kind": "text", "text": "verdict"}]}],
    }
    rpc_resp = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"jsonrpc": "2.0", "id": "1", "result": completed}),
    )
    client = A2ACheckerClient("http://localhost:2025")
    client._rpc_url = "http://localhost:2025/a2a/uuid"  # noqa: SLF001

    with patch("course_companion.subagents.a2a_checker.httpx.Client") as factory:
        factory.return_value = _mock_client(post_side_effect=[rpc_resp])
        task = client.get_task("t1")

    assert client.map_task_status(task) == "success"
    assert client.extract_result_text(task) == "verdict"


def test_jsonrpc_error_raises() -> None:
    rpc_resp = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"jsonrpc": "2.0", "id": "1", "error": {"message": "nope"}}),
    )
    client = A2ACheckerClient("http://localhost:2025")
    client._rpc_url = "http://localhost:2025/a2a/uuid"  # noqa: SLF001

    with patch("course_companion.subagents.a2a_checker.httpx.Client") as factory:
        factory.return_value = _mock_client(post_side_effect=[rpc_resp])
        with pytest.raises(A2ACheckerError, match="nope"):
            client.get_task("t1")
