"""Upload agent system prompts from repo files into Langfuse Prompt Management."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import httpx
from langfuse import Langfuse

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.agent.prompt_registry import PROMPT_FILES, load_named_prompt
from app.env_loader import load_repo_env, resolve_langfuse_keys
from app.integrations.langfuse_prompt_labels import transfer_deployment_label


def _wait_for_health(host: str, wait_sec: float) -> None:
    deadline = time.monotonic() + wait_sec
    url = f"{host.rstrip('/')}/api/public/health"
    while time.monotonic() < deadline:
        try:
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(2.0)
    msg = f"Langfuse health check failed: {url}"
    raise RuntimeError(msg)


def _upload_prompts(
    *,
    label: str,
    commit_message: str,
    active_name: str,
    upload_all: bool,
) -> list[tuple[str, int]]:
    load_repo_env()
    host, public_key, secret_key = resolve_langfuse_keys()
    _wait_for_health(host, wait_sec=60.0)

    client = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    client.auth_check()

    names = sorted(PROMPT_FILES) if upload_all else [active_name]
    if active_name not in PROMPT_FILES:
        msg = f"Unknown prompt name: {active_name}"
        raise ValueError(msg)

    transfer_deployment_label(
        client,
        label=label,
        owner_name=active_name,
        other_names=sorted(PROMPT_FILES),
    )

    uploaded: list[tuple[str, int]] = []
    for name in names:
        text = load_named_prompt(name)
        labels = [label] if name == active_name else []
        prompt_client = client.create_prompt(
            name=name,
            prompt=text,
            labels=labels,
            type="text",
            commit_message=commit_message,
        )
        uploaded.append((name, prompt_client.version))

    client.flush()
    return uploaded


def main() -> None:
    load_repo_env()
    default_name = os.environ.get("PROMPT_NAME", "SYSTEM_PROMPT_SEARCH_FALLBACK")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--name",
        default=default_name,
        help="Prompt that receives the deployment label (default: PROMPT_NAME env)",
    )
    parser.add_argument(
        "--label",
        default=os.environ.get("PROMPT_LABEL", "production"),
        help="Deployment label for --name (default: PROMPT_LABEL env)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Upload all registry prompts; only --name gets --label",
    )
    parser.add_argument(
        "--commit-message",
        default="sync from backend/app/agent/prompts",
        help="Version commit message in Langfuse",
    )
    args = parser.parse_args()

    host, _, _ = resolve_langfuse_keys()
    uploaded = _upload_prompts(
        label=args.label,
        commit_message=args.commit_message,
        active_name=args.name,
        upload_all=args.all,
    )
    print(f"langfuse_host: {host}")
    print(f"active_prompt: {args.name}")
    print(f"label: {args.label} (on {args.name} only among registry prompts)")
    for name, version in uploaded:
        tagged = " [label]" if name == args.name else ""
        print(f"prompt: {name} -> v{version}{tagged}")
    print(f"uploaded_count: {len(uploaded)}")


if __name__ == "__main__":
    main()
