"""Smoke checks for a running Agent Core (and optional Langfuse)."""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any

import httpx

DEFAULT_SESSION_ID = "550e8400-e29b-41d4-a716-446655440000"
DEFAULT_MESSAGE = "Какой курс для новичка?"
CHAT_TIMEOUT_SEC = float(os.getenv("CHECK_CHAT_TIMEOUT_SEC", "120"))
STREAM_TIMEOUT_SEC = float(os.getenv("CHECK_STREAM_TIMEOUT_SEC", "120"))
LANGFUSE_WAIT_SEC = float(os.getenv("CHECK_LANGFUSE_WAIT_SEC", "180"))
LANGFUSE_RETRY_SEC = float(os.getenv("CHECK_LANGFUSE_RETRY_SEC", "5"))


def _backend_url() -> str:
    return os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def _langfuse_url() -> str:
    return os.getenv("LANGFUSE_HOST", "http://localhost:3001").rstrip("/")


def _ok(message: str) -> None:
    print(f"OK: {message}")


def _fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_health(client: httpx.Client) -> None:
    response = client.get("/health")
    if response.status_code != 200:
        _fail(f"GET /health -> {response.status_code}: {response.text}")
    payload = response.json()
    for key in ("status", "version", "rag_indexed_docs", "sessions_active"):
        if key not in payload:
            _fail(f"GET /health missing field: {key}")
    status = payload["status"]
    docs = payload["rag_indexed_docs"]
    _ok(f"GET /health -> status={status}, rag_indexed_docs={docs}")


def check_reindex(client: httpx.Client) -> None:
    response = client.post("/admin/reindex")
    if response.status_code == 404:
        _fail("POST /admin/reindex -> 404 (нужен ENV=dev)")
    if response.status_code != 200:
        _fail(f"POST /admin/reindex -> {response.status_code}: {response.text}")
    payload = response.json()
    for key in ("indexed", "skipped", "removed"):
        if key not in payload:
            _fail(f"POST /admin/reindex missing field: {key}")
    _ok(
        "POST /admin/reindex -> "
        f"indexed={payload['indexed']}, skipped={payload['skipped']}, removed={payload['removed']}",
    )


def check_chat_telegram(client: httpx.Client, *, message: str) -> None:
    body = {
        "session_id": DEFAULT_SESSION_ID,
        "channel": "telegram",
        "message": message,
    }
    response = client.post("/api/v1/chat", json=body)
    if response.status_code != 200:
        _fail(f"POST /api/v1/chat -> {response.status_code}: {response.text}")
    payload = response.json()
    for key in ("session_id", "reply", "format"):
        if key not in payload:
            _fail(f"POST /api/v1/chat missing field: {key}")
    if payload["format"] != "markdown":
        _fail(f"POST /api/v1/chat format={payload['format']}, expected markdown")
    if not payload["reply"].strip():
        _fail("POST /api/v1/chat returned empty reply")
    preview = payload["reply"][:80].replace("\n", " ")
    _ok(f"POST /api/v1/chat (telegram) -> reply preview: {preview!r}...")


def check_chat_stream(client: httpx.Client, *, message: str) -> None:
    body = {
        "session_id": DEFAULT_SESSION_ID,
        "channel": "web",
        "message": message,
    }
    with client.stream(
        "POST",
        "/api/v1/chat/stream",
        json=body,
        timeout=STREAM_TIMEOUT_SEC,
    ) as response:
        if response.status_code != 200:
            _fail(f"POST /api/v1/chat/stream -> {response.status_code}: {response.read().decode()}")
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" not in content_type:
            _fail(f"POST /api/v1/chat/stream content-type={content_type!r}")

        events: list[str] = []
        for line in response.iter_lines():
            if line.startswith("event: "):
                events.append(line.removeprefix("event: ").strip())

        required = {"token", "done"}
        missing = required - set(events)
        if missing:
            _fail(f"SSE missing events: {sorted(missing)}; got: {events}")
    _ok(f"POST /api/v1/chat/stream -> events: {', '.join(events)}")


def check_langfuse(*, wait: bool = True) -> None:
    url = f"{_langfuse_url()}/api/public/health"
    deadline = time.monotonic() + (LANGFUSE_WAIT_SEC if wait else 0)
    last_status: int | None = None
    last_body = ""
    last_error = ""

    while True:
        try:
            response = httpx.get(url, timeout=10.0, trust_env=False)
            last_status = response.status_code
            last_body = response.text.strip()
            if response.status_code == 200:
                _ok(f"Langfuse health -> {url}")
                return
            if response.status_code == 503 and wait and time.monotonic() < deadline:
                print(
                    f"WAIT: Langfuse ещё стартует (503). Повтор через {LANGFUSE_RETRY_SEC:.0f}s...",
                )
                time.sleep(LANGFUSE_RETRY_SEC)
                continue
            _fail(f"Langfuse health -> {response.status_code}: {last_body or '(empty)'}")
        except httpx.HTTPError as exc:
            last_error = str(exc)
            if wait and time.monotonic() < deadline:
                retry_sec = LANGFUSE_RETRY_SEC
                print(f"WAIT: Langfuse недоступен ({exc}). Повтор через {retry_sec:.0f}s...")
                time.sleep(LANGFUSE_RETRY_SEC)
                continue
            _fail(f"Langfuse health request failed: {exc}")

        if not wait or time.monotonic() >= deadline:
            hint = (
                "Запустите `make up`, подождите 1–3 мин и повторите. "
                "Логи: `make compose logs langfuse-web`"
            )
            details = last_body or last_error or "нет ответа"
            _fail(
                f"Langfuse не готов за {LANGFUSE_WAIT_SEC:.0f}s "
                f"(last status={last_status}): {details}. {hint}",
            )


def _run_checks(checks: list[str], *, message: str) -> None:
    base = _backend_url()
    print(f"Backend: {base}")
    timeout = httpx.Timeout(CHAT_TIMEOUT_SEC, connect=10.0)
    with httpx.Client(base_url=base, timeout=timeout, trust_env=False) as client:
        dispatch: dict[str, Any] = {
            "health": lambda: check_health(client),
            "reindex": lambda: check_reindex(client),
            "chat": lambda: check_chat_telegram(client, message=message),
            "chat-stream": lambda: check_chat_stream(client, message=message),
        }
        for check in checks:
            print(f"-- {check}")
            dispatch[check]()

    _ok(f"all checks passed ({', '.join(checks)})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-check Agent Core HTTP API")
    parser.add_argument(
        "command",
        choices=["health", "reindex", "chat", "chat-stream", "langfuse", "api"],
        help="check to run",
    )
    parser.add_argument(
        "--message",
        default=DEFAULT_MESSAGE,
        help="user message for chat checks",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="do not retry langfuse health (single attempt)",
    )
    args = parser.parse_args()

    if args.command == "langfuse":
        check_langfuse(wait=not args.no_wait)
        _ok("langfuse check passed")
        return

    if args.command == "api":
        checks = ["health", "reindex", "chat", "chat-stream"]
        _run_checks(checks, message=args.message)
        print("-- langfuse")
        check_langfuse(wait=not args.no_wait)
        _ok("api + langfuse checks passed")
        return

    _run_checks([args.command], message=args.message)


if __name__ == "__main__":
    main()
