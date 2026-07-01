"""Neo4j driver factory, URI resolution, and connectivity checks."""

from __future__ import annotations

import logging
import platform
import socket
import subprocess
from urllib.parse import ParseResult, urlparse

from neo4j import Auth, Driver, GraphDatabase, basic_auth

from app.exceptions import ProviderUnavailableError

logger = logging.getLogger(__name__)

_driver: Driver | None = None
_driver_key: tuple[str, str, str] | None = None

_DEFAULT_BOLT_PORT = 7687
_CONNECT_TIMEOUT_SEC = 10.0
_PROBE_TIMEOUT_SEC = 3.0


def resolve_neo4j_uri(uri: str, *, fail_fast: bool = False) -> str:
    """Pick a reachable Bolt URI; on Windows prefer WSL IP over dead localhost."""
    parsed = urlparse(uri)
    scheme = parsed.scheme or "bolt"
    if scheme not in {"bolt", "bolt+s", "bolt+ssc", "neo4j", "neo4j+s", "neo4j+ssc"}:
        return uri

    host = parsed.hostname or "localhost"
    port = parsed.port or _DEFAULT_BOLT_PORT

    if platform.system() != "Windows" or host not in {"localhost", "127.0.0.1"}:
        if fail_fast and not _bolt_reachable(uri):
            _raise_unreachable(uri)
        return uri

    candidates = [_build_bolt_uri(scheme, "127.0.0.1", port, parsed)]
    wsl_ip = _wsl_host_ip()
    if wsl_ip:
        candidates.append(_build_bolt_uri(scheme, wsl_ip, port, parsed))

    for candidate in candidates:
        if _bolt_reachable(candidate):
            if candidate != uri.rstrip("/"):
                logger.info(
                    "Neo4j localhost unreachable from Windows; using WSL host",
                    extra={"neo4j_uri": candidate},
                )
            return candidate

    if fail_fast:
        _raise_unreachable(uri, wsl_ip=wsl_ip)
    return uri


def ensure_neo4j_uri(uri: str) -> str:
    """Resolve URI and fail fast when Neo4j is not reachable."""
    return resolve_neo4j_uri(uri, fail_fast=True)


def create_driver(uri: str, user: str, password: str) -> Driver:
    """Create a Neo4j driver with resolved URI and basic auth."""
    resolved = resolve_neo4j_uri(uri)
    auth: Auth = basic_auth(user, password)
    return GraphDatabase.driver(
        resolved,
        auth=auth,
        connection_timeout=_CONNECT_TIMEOUT_SEC,
    )


def get_neo4j_driver(
    settings: object | None = None,
    *,
    uri: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> Driver:
    """Return a process-wide cached Neo4j driver."""
    global _driver, _driver_key

    if settings is not None:
        uri = uri or getattr(settings, "neo4j_uri", "")
        user = user or getattr(settings, "neo4j_user", "neo4j")
        password = password or getattr(settings, "neo4j_password", "")

    if not uri or user is None or password is None:
        msg = "Neo4j connection settings are required"
        raise ValueError(msg)

    key = (uri, user, password)
    if _driver is None or _driver_key != key:
        if _driver is not None:
            _driver.close()
        _driver = create_driver(uri, user, password)
        _driver_key = key
    return _driver


def reset_neo4j_driver() -> None:
    """Close cached driver (tests)."""
    global _driver, _driver_key
    if _driver is not None:
        _driver.close()
    _driver = None
    _driver_key = None


def verify_connectivity(uri: str, user: str, password: str) -> None:
    """Verify Bolt connectivity; raises on failure."""
    driver = create_driver(uri, user, password)
    try:
        driver.verify_connectivity()
    finally:
        driver.close()


def _build_bolt_uri(scheme: str, host: str, port: int, parsed: ParseResult) -> str:
    userinfo = ""
    if parsed.username:
        userinfo = parsed.username
        if parsed.password:
            userinfo = f"{userinfo}:{parsed.password}"
        userinfo = f"{userinfo}@"
    path = parsed.path if parsed.path and parsed.path != "/" else ""
    return f"{scheme}://{userinfo}{host}:{port}{path}"


def _bolt_reachable(uri: str) -> bool:
    parsed = urlparse(uri)
    host = parsed.hostname or "localhost"
    port = parsed.port or _DEFAULT_BOLT_PORT
    try:
        with socket.create_connection((host, port), timeout=_PROBE_TIMEOUT_SEC):
            return True
    except OSError:
        return False


def _wsl_host_ip() -> str | None:
    try:
        result = subprocess.run(
            ["wsl", "hostname", "-I"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    parts = result.stdout.strip().split()
    return parts[0] if parts else None


def _raise_unreachable(uri: str, *, wsl_ip: str | None = None) -> None:
    hint = (
        "Поднимите Neo4j: .\\make.ps1 graph-up (или make graph-up в WSL) "
        "и дождитесь status=healthy. "
        "На Windows с Docker в WSL укажите NEO4J_URI=bolt://<wsl-ip>:7687 "
        "(wsl hostname -I)."
    )
    if wsl_ip:
        hint = f"Neo4j недоступен по {uri} и bolt://{wsl_ip}:{_DEFAULT_BOLT_PORT}. " + hint
    raise ProviderUnavailableError(message=hint, error_code="neo4j_unreachable")
