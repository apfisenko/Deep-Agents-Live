from __future__ import annotations

import logging

from homework_mentor.logging_setup import SecretRedactFilter, redact_secrets, setup_logging


def test_redact_secrets_masks_openrouter_key() -> None:
    text = "OPENROUTER_API_KEY=sk-or-v1-supersecretvalue"
    redacted = redact_secrets(text)
    assert "supersecretvalue" not in redacted
    assert "***" in redacted


def test_redact_filter_on_log_record() -> None:
    record = logging.LogRecord(
        name="homework_mentor",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="token=sk-or-v1-abc123xyz bearer Bearer sk-or-v1-abc123xyz",
        args=(),
        exc_info=None,
    )
    assert SecretRedactFilter().filter(record) is True
    rendered = str(record.msg)
    assert "abc123xyz" not in rendered
    assert "***" in rendered


def test_setup_logging_writes_service_and_redacts(tmp_path) -> None:
    logger = setup_logging(level="INFO", log_to_file=True, logs_dir=tmp_path)
    logger.info("boot OPENROUTER_API_KEY=sk-or-v1-should-not-leak")
    log_text = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "service=homework_mentor" in log_text
    assert "should-not-leak" not in log_text
    assert "OPENROUTER_API_KEY=***" in log_text
