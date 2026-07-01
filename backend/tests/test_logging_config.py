"""Logging configuration tests."""

import logging

import pytest

from app.logging_config import configure_logging


def test_configure_logging_dev_includes_timestamp(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO", env="dev")
    logging.getLogger("test.logging").info("hello")
    captured = capsys.readouterr()
    assert captured.err.count("-") >= 2
    assert "INFO:test.logging:hello" in captured.err
