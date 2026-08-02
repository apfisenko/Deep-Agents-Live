"""Unit-тесты CLI-тегов [mode] и [router]."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

from course_companion.cli import _find_mode_in_update, _ModeTracker, _print_chunk


def test_find_mode_in_update_router_nested() -> None:
    update = {"router": {"mode": "homework", "last_intent": "homework"}}
    assert _find_mode_in_update(update) == "homework"


def test_find_mode_in_update_tools_command() -> None:
    update = {"mode": "review", "messages": []}
    assert _find_mode_in_update(update) == "review"


def test_mode_tracker_prints_transition() -> None:
    buf = io.StringIO()
    with redirect_stdout(buf):
        tracker = _ModeTracker("qa")
        tracker.observe({"router": {"mode": "homework"}})
    assert "[mode]   qa → homework" in buf.getvalue()


def test_mode_tracker_skips_same_mode() -> None:
    buf = io.StringIO()
    with redirect_stdout(buf):
        t = _ModeTracker("homework")
        t.observe({"router": {"mode": "homework"}})
    assert buf.getvalue() == ""


def test_print_chunk_emits_mode_on_router_update() -> None:
    buf = io.StringIO()
    tracker = _ModeTracker("qa")
    with redirect_stdout(buf):
        _print_chunk(((), {"router": {"mode": "homework", "last_intent": "homework"}}), tracker)
    output = buf.getvalue()
    assert "[router] → homework" in output
    assert "[mode]   qa → homework" in output
    assert tracker.mode == "homework"
