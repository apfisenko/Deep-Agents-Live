"""A2A-клиент чужого checker: discovery, message/send, tasks/get, tasks/cancel."""

from __future__ import annotations

import logging
import uuid
from typing import Any
from urllib.parse import urlparse

import httpx

from course_companion.checker_config import a2a_checker_graph_id

logger = logging.getLogger(__name__)

_HTTP_OK = 200

A2A_AGENT_NAME = "homework-checker-async"

A2A_STATE_TO_STATUS: dict[str, str] = {
    "submitted": "pending",
    "working": "running",
    "input-required": "running",
    "completed": "success",
    "failed": "error",
    "canceled": "cancelled",
}


class A2ACheckerError(Exception):
    """Ошибка A2A JSON-RPC или discovery."""


class A2ACheckerClient:
    """HTTP-клиент A2A v1.0 для фоновой проверки домашек."""

    def __init__(
        self,
        base_url: str,
        *,
        graph_id: str | None = None,
        timeout: float = 600.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.graph_id = graph_id or a2a_checker_graph_id()
        self.timeout = timeout
        self._card: dict[str, Any] | None = None
        self._rpc_url: str | None = None

    def discover(self, *, force: bool = False) -> dict[str, Any]:
        """GET /.well-known/agent-card.json с кешированием."""
        if self._card is not None and not force:
            return self._card

        card = self._fetch_agent_card()
        rpc_url = card.get("url") or _first_interface_url(card)
        if not rpc_url:
            msg = "Agent card has no JSON-RPC url"
            raise A2ACheckerError(msg)

        self._card = card
        self._rpc_url = rpc_url
        return card

    @property
    def rpc_url(self) -> str:
        if self._rpc_url is None:
            self.discover()
        if self._rpc_url is None:
            msg = "A2A RPC url not resolved after discovery"
            raise A2ACheckerError(msg)
        return self._rpc_url

    @property
    def rpc_path(self) -> str:
        """Относительный путь RPC-endpoint (для фронтового поллера)."""
        parsed = urlparse(self.rpc_url)
        if parsed.path:
            return parsed.path
        return self.rpc_url.removeprefix(self.base_url)

    def send_message(
        self,
        text: str,
        *,
        task_id: str | None = None,
        context_id: str | None = None,
    ) -> dict[str, Any]:
        """JSON-RPC message/send — запуск или follow-up задачи."""
        params: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "messageId": f"msg-{uuid.uuid4().hex[:12]}",
            },
        }
        if task_id:
            params["message"]["taskId"] = task_id
        if context_id:
            params["message"]["contextId"] = context_id
        return self._jsonrpc("message/send", params)

    def get_task(self, task_id: str) -> dict[str, Any]:
        """JSON-RPC tasks/get."""
        return self._jsonrpc("tasks/get", {"id": task_id})

    def cancel_task(self, task_id: str) -> dict[str, Any]:
        """JSON-RPC tasks/cancel."""
        return self._jsonrpc("tasks/cancel", {"id": task_id})

    def map_task_status(self, task: dict[str, Any]) -> str:
        """A2A state → статус async_tasks (pending/running/success/...)."""
        status = task.get("status") or {}
        state = status.get("state", "working") if isinstance(status, dict) else str(status)
        return A2A_STATE_TO_STATUS.get(state, "running")

    def extract_result_text(self, task: dict[str, Any]) -> str:
        """Текст вердикта из artifacts или history."""
        for artifact in task.get("artifacts") or []:
            for part in artifact.get("parts") or []:
                if part.get("kind") == "text" and part.get("text"):
                    return str(part["text"])
        for message in reversed(task.get("history") or []):
            if message.get("role") != "agent":
                continue
            for part in message.get("parts") or []:
                if part.get("kind") == "text" and part.get("text"):
                    return str(part["text"])
        return "(completed with no text artifacts)"

    def _fetch_agent_card(self) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/.well-known/agent-card.json")
            if resp.status_code == _HTTP_OK:
                return resp.json()

            assistant_id = self._resolve_assistant_id(client)
            resp = client.get(
                f"{self.base_url}/.well-known/agent-card.json",
                params={"assistant_id": assistant_id},
            )
            resp.raise_for_status()
            return resp.json()

    def _resolve_assistant_id(self, client: httpx.Client) -> str:
        resp = client.post(f"{self.base_url}/assistants/search", json={})
        resp.raise_for_status()
        assistants = resp.json()
        for item in assistants:
            if item.get("graph_id") == self.graph_id:
                assistant_id = item.get("assistant_id")
                if assistant_id:
                    return str(assistant_id)
        msg = f"No assistant with graph_id={self.graph_id!r} on {self.base_url}"
        raise A2ACheckerError(msg)

    def _jsonrpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": f"cc-{uuid.uuid4().hex[:8]}",
            "method": method,
            "params": params,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.rpc_url, json=payload)
            resp.raise_for_status()
            body = resp.json()
        if "error" in body:
            err = body["error"]
            message = err.get("message", err) if isinstance(err, dict) else err
            raise A2ACheckerError(str(message))
        result = body.get("result")
        if not isinstance(result, dict):
            msg = f"Unexpected A2A result for {method}: {result!r}"
            raise A2ACheckerError(msg)
        return result


def _first_interface_url(card: dict[str, Any]) -> str | None:
    for iface in card.get("supportedInterfaces") or []:
        url = iface.get("url")
        if url:
            return str(url)
    return None
