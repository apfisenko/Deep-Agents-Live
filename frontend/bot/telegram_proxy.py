"""Telegram API proxy resolution (explicit env + Windows system proxy)."""

from __future__ import annotations

import sys
from typing import Literal

from config import Settings

ProxySource = Literal["env", "windows", "none"]


def normalize_explicit_proxy(raw: str) -> str | None:
    value = raw.strip()
    if not value:
        return None
    if "://" in value:
        return value
    if value.isdigit():
        return f"http://127.0.0.1:{value}"
    if ":" in value:
        return f"http://{value}"
    return None


def normalize_proxy_server(raw: str) -> str | None:
    value = raw.strip()
    if not value:
        return None
    if "://" in value:
        return value

    parts: dict[str, str] = {}
    for segment in value.split(";"):
        segment = segment.strip()
        if not segment:
            continue
        if "=" in segment:
            scheme, hostport = segment.split("=", 1)
            parts[scheme.lower()] = hostport.strip()
        else:
            parts["http"] = segment

    resolved = parts.get("https") or parts.get("http")
    if resolved is None:
        return None
    return f"http://{resolved}"


def detect_windows_system_proxy() -> str | None:
    if sys.platform != "win32":
        return None

    import winreg

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        )
        enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
        if not enabled:
            return None
        server, _ = winreg.QueryValueEx(key, "ProxyServer")
    except OSError:
        return None
    return normalize_proxy_server(str(server))


def resolve_telegram_proxy(settings: Settings) -> tuple[str | None, ProxySource]:
    raw_explicit = settings.telegram_proxy.strip() if settings.telegram_proxy else None
    if raw_explicit:
        explicit = normalize_explicit_proxy(raw_explicit) or normalize_proxy_server(raw_explicit)
        if explicit:
            return explicit, "env"

    detected = detect_windows_system_proxy()
    if detected:
        return detected, "windows"

    return None, "none"
