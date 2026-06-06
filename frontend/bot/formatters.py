"""Markdown to Telegram HTML formatter."""

from __future__ import annotations

import html
import re

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_CODE_RE = re.compile(r"`([^`]+)`")


def escape_html(text: str) -> str:
    return html.escape(text, quote=False)


def markdown_to_telegram_html(text: str) -> str:
    if not text.strip():
        return ""

    parts: list[str] = []
    cursor = 0
    for match in _LINK_RE.finditer(text):
        parts.append(_format_plain_segment(text[cursor : match.start()]))
        label = escape_html(match.group(1))
        url = escape_html(match.group(2))
        parts.append(f'<a href="{url}">{label}</a>')
        cursor = match.end()
    parts.append(_format_plain_segment(text[cursor:]))
    return "".join(parts)


def _format_plain_segment(segment: str) -> str:
    if not segment:
        return ""

    placeholders: list[str] = []

    def stash_code(match: re.Match[str]) -> str:
        placeholders.append(f"<code>{escape_html(match.group(1))}</code>")
        return f"\x00CODE{len(placeholders) - 1}\x00"

    def stash_bold(match: re.Match[str]) -> str:
        placeholders.append(f"<b>{escape_html(match.group(1))}</b>")
        return f"\x00BOLD{len(placeholders) - 1}\x00"

    working = _CODE_RE.sub(stash_code, segment)
    working = _BOLD_RE.sub(stash_bold, working)
    escaped = escape_html(working)

    for index, value in enumerate(placeholders):
        escaped = escaped.replace(f"\x00CODE{index}\x00", value)
        escaped = escaped.replace(f"\x00BOLD{index}\x00", value)
    return escaped
