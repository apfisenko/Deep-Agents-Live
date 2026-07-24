from __future__ import annotations

import pytest

from homework_mentor.errors import describe_exception, is_transient_provider_error


class _FakeResponseError(Exception):
    def __init__(self, message: str, *, status_code: int, body: dict[str, str]) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def test_describe_exception_includes_body() -> None:
    exc = _FakeResponseError(
        "Provider returned error",
        status_code=502,
        body={"error": {"message": "upstream timeout"}},
    )
    text = describe_exception(exc)
    assert "Provider returned error" in text
    assert "upstream timeout" in text


def test_describe_exception_unwraps_cause() -> None:
    root = ValueError("root cause")
    wrapped = RuntimeError("wrapper")
    wrapped.__cause__ = root
    assert describe_exception(wrapped) == "wrapper -> root cause"


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Provider returned error", True),
        ("HTTP 429 Too Many Requests", True),
        ("invalid API key", False),
    ],
)
def test_is_transient_provider_error(*, message: str, expected: bool) -> None:
    assert is_transient_provider_error(RuntimeError(message)) is expected
