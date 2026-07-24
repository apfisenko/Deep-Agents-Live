"""Logging setup with secret redaction."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Final

from homework_mentor.config import project_root

if TYPE_CHECKING:
    from pathlib import Path

SERVICE_NAME: Final = "homework_mentor"

_SECRET_PATTERNS: Final = (
    re.compile(r"(OPENROUTER_API_KEY\s*[=:]\s*)(\S+)", re.IGNORECASE),
    re.compile(r"(sk-or-v1-)[A-Za-z0-9_-]+"),
    re.compile(r"(Bearer\s+)([A-Za-z0-9._\-]+)", re.IGNORECASE),
)


class SecretRedactFilter(logging.Filter):
    """Redact API keys and bearer tokens from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: _redact(str(v)) for k, v in record.args.items()}
            else:
                record.args = tuple(_redact(str(arg)) for arg in record.args)
        return True


def _redact(text: str) -> str:
    redacted = text
    for pattern in _SECRET_PATTERNS:
        if pattern.groups == 2:  # noqa: PLR2004
            redacted = pattern.sub(r"\1***", redacted)
        else:
            redacted = pattern.sub(r"\1***", redacted)
    return redacted


def redact_secrets(text: str) -> str:
    """Public helper for tests and callers that format strings manually."""
    return _redact(text)


def setup_logging(
    *,
    level: str = "INFO",
    log_to_file: bool = True,
    logs_dir: Path | None = None,
) -> logging.Logger:
    """Configure package logger: stdout (+ optional `logs/app.log`)."""
    logger = logging.getLogger(SERVICE_NAME)
    logger.handlers.clear()
    logger.setLevel(level.upper())
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s service=%(service)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    class _ServiceFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.service = SERVICE_NAME
            return True

    service_filter = _ServiceFilter()
    redact_filter = SecretRedactFilter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(service_filter)
    stream_handler.addFilter(redact_filter)
    logger.addHandler(stream_handler)

    if log_to_file:
        directory = logs_dir or (project_root() / "logs")
        directory.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            directory / "app.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(service_filter)
        file_handler.addFilter(redact_filter)
        logger.addHandler(file_handler)

    return logger
