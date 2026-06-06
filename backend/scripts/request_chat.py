"""Raw chat API requests (curl-like output)."""

from __future__ import annotations

import argparse
import os
import sys

import httpx

DEFAULT_SESSION_ID = "550e8400-e29b-41d4-a716-446655440000"
DEFAULT_MESSAGE = "Какой курс для новичка?"
TIMEOUT_SEC = float(os.getenv("CHAT_TIMEOUT_SEC", "120"))


def _backend_url() -> str:
    return os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def _message() -> str:
    return os.getenv("CHAT_MESSAGE", DEFAULT_MESSAGE)


def request_telegram() -> None:
    body = {
        "session_id": DEFAULT_SESSION_ID,
        "channel": "telegram",
        "message": _message(),
    }
    response = httpx.post(
        f"{_backend_url()}/api/v1/chat",
        json=body,
        timeout=TIMEOUT_SEC,
        trust_env=False,
    )
    sys.stdout.write(response.text)
    if not response.text.endswith("\n"):
        sys.stdout.write("\n")
    if response.status_code >= 400:
        raise SystemExit(1)


def request_stream() -> None:
    body = {
        "session_id": DEFAULT_SESSION_ID,
        "channel": "web",
        "message": _message(),
    }
    with httpx.stream(
        "POST",
        f"{_backend_url()}/api/v1/chat/stream",
        json=body,
        timeout=TIMEOUT_SEC,
        trust_env=False,
    ) as response:
        if response.status_code >= 400:
            sys.stderr.write(response.read().decode())
            raise SystemExit(1)
        for line in response.iter_lines():
            print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send chat request and print raw response")
    parser.add_argument(
        "command",
        choices=["telegram", "stream"],
        help="telegram = JSON reply, stream = SSE events",
    )
    args = parser.parse_args()
    if args.command == "telegram":
        request_telegram()
    else:
        request_stream()


if __name__ == "__main__":
    main()
