"""Resolve system prompt text from run config."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from app.agent.prompt_registry import PROMPT_FILES, load_named_prompt
from app.agent.run_config import PromptSection
from app.config import Settings, get_settings
from app.exceptions import ConfigNotFoundError
from app.integrations.langfuse import get_langfuse_client
from app.integrations.langfuse_prompt_labels import resolve_prompt_name_for_label
from app.paths import REPO_ROOT

logger = logging.getLogger(__name__)


def _parse_iso_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _fetch_version_updated_at(client: Any, *, name: str, label: str) -> datetime | None:
    """Best-effort Langfuse version timestamp (createdAt / updatedAt from API extras)."""
    try:
        raw = client.api.prompts.get(prompt_name=name, label=label)
    except (LookupError, OSError, RuntimeError, TypeError, ValueError):
        logger.debug(
            "Could not fetch Langfuse prompt metadata",
            extra={"prompt_name": name, "label": label},
            exc_info=True,
        )
        return None
    extra = getattr(raw, "__pydantic_extra__", None) or {}
    for key in ("updatedAt", "createdAt", "lastUpdatedAt", "last_updated_at"):
        parsed = _parse_iso_datetime(extra.get(key))
        if parsed is not None:
            return parsed
    return None


@dataclass(frozen=True)
class ResolvedPrompt:
    text: str
    source: Literal["file", "langfuse"]
    name: str
    version: int | None = None
    label: str | None = None
    version_updated_at: datetime | None = None
    langfuse_prompt: Any | None = None

    @property
    def linkable(self) -> bool:
        return self.langfuse_prompt is not None and not getattr(
            self.langfuse_prompt,
            "is_fallback",
            False,
        )


def _resolve_repo_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def _load_prompt_file(path_str: str) -> str:
    path = _resolve_repo_path(path_str)
    if not path.is_file():
        msg = f"Prompt file not found: {path}"
        raise ConfigNotFoundError(msg, config_id=path_str)
    return path.read_text(encoding="utf-8").strip()


def _file_fallback_text(prompt: PromptSection) -> str | None:
    if prompt.name in PROMPT_FILES:
        return load_named_prompt(prompt.name)
    if prompt.path:
        resolved = _resolve_repo_path(prompt.path)
        if resolved.is_file() and resolved.suffix != ".py":
            return _load_prompt_file(prompt.path)
    return None


def _resolve_langfuse_fallback_text(
    prompt: PromptSection,
    *,
    settings: Settings | None = None,
) -> str | None:
    """Default prompt when Langfuse is unavailable (PROMPT_FALLBACK_PATH in .env)."""
    cfg = settings or get_settings()
    fallback_path = cfg.prompt_fallback_path.strip()
    if fallback_path:
        try:
            return _load_prompt_file(fallback_path)
        except ConfigNotFoundError:
            logger.warning(
                "PROMPT_FALLBACK_PATH not found; trying prompt.path / registry",
                extra={"path": fallback_path},
            )
    return _file_fallback_text(prompt)


def _resolve_file_prompt(prompt: PromptSection) -> ResolvedPrompt:
    if prompt.path:
        resolved = _resolve_repo_path(prompt.path)
        if resolved.is_file() and resolved.suffix != ".py":
            return ResolvedPrompt(
                text=_load_prompt_file(prompt.path),
                source="file",
                name=prompt.name,
            )
    if prompt.name in PROMPT_FILES:
        return ResolvedPrompt(
            text=load_named_prompt(prompt.name),
            source="file",
            name=prompt.name,
        )
    msg = f"Unknown file prompt name: {prompt.name}"
    raise ConfigNotFoundError(msg, config_id=prompt.name)


def _resolve_langfuse_prompt(
    prompt: PromptSection,
    *,
    settings: Settings | None = None,
) -> ResolvedPrompt:
    label = prompt.label or "production"
    fallback = _resolve_langfuse_fallback_text(prompt, settings=settings)
    client = get_langfuse_client(settings)
    if client is None:
        if fallback is None:
            msg = f"Langfuse unavailable and no file fallback for prompt: {prompt.name}"
            raise ConfigNotFoundError(msg, config_id=prompt.name)
        logger.warning(
            "Langfuse unavailable; using file fallback for prompt",
            extra={"prompt_name": prompt.name, "label": label},
        )
        return ResolvedPrompt(
            text=fallback,
            source="file",
            name=prompt.name,
            label=label,
        )

    try:
        resolve_prompt_name_for_label(
            client,
            label=label,
            expected_name=prompt.name,
        )
        langfuse_prompt = client.get_prompt(prompt.name, label=label, fallback=fallback)
    except ConfigNotFoundError:
        raise
    except Exception:
        logger.exception(
            "Failed to fetch Langfuse prompt",
            extra={"prompt_name": prompt.name, "label": label},
        )
        if fallback is None:
            msg = f"Langfuse prompt fetch failed and no file fallback: {prompt.name}"
            raise ConfigNotFoundError(msg, config_id=prompt.name) from None
        return ResolvedPrompt(
            text=fallback,
            source="file",
            name=prompt.name,
            label=label,
        )

    text = langfuse_prompt.prompt
    if getattr(langfuse_prompt, "is_fallback", False):
        logger.warning(
            "Langfuse prompt fallback used (no link-to-traces)",
            extra={"prompt_name": prompt.name, "label": label},
        )
    version_updated_at = None
    if not getattr(langfuse_prompt, "is_fallback", False):
        version_updated_at = _fetch_version_updated_at(client, name=prompt.name, label=label)
    return ResolvedPrompt(
        text=text,
        source="langfuse",
        name=prompt.name,
        version=langfuse_prompt.version,
        label=label,
        version_updated_at=version_updated_at,
        langfuse_prompt=langfuse_prompt,
    )


def resolve_prompt(
    prompt: PromptSection,
    *,
    settings: Settings | None = None,
) -> ResolvedPrompt:
    if prompt.source == "file":
        return _resolve_file_prompt(prompt)
    return _resolve_langfuse_prompt(prompt, settings=settings)
