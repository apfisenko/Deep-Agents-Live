"""Sync dataset manifests to Langfuse (E-16 folders-as-versions)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from base64 import b64encode
from pathlib import Path

from env_loader import load_repo_env, resolve_langfuse_keys
from models import (
    discover_manifests,
    langfuse_dataset_name,
    load_manifest,
    manifest_to_langfuse_item,
    validate_manifest,
)


def _load_env() -> None:
    load_repo_env()


def _auth_headers(public_key: str, secret_key: str) -> dict[str, str]:
    token = b64encode(f"{public_key}:{secret_key}".encode()).decode()
    return {
        "Content-Type": "application/json",
        "Authorization": f"Basic {token}",
    }


def _api_request(method: str, url: str, body: dict | None, headers: dict[str, str]) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        msg = f"{method} {url} -> {exc.code}: {detail}"
        raise RuntimeError(msg) from exc


def auth_check(host: str, public_key: str, secret_key: str) -> None:
    url = f"{host.rstrip('/')}/api/public/health"
    headers = _auth_headers(public_key, secret_key)
    _api_request("GET", url, None, headers)


def ensure_dataset(host: str, headers: dict[str, str], name: str, description: str) -> None:
    url = f"{host.rstrip('/')}/api/public/v2/datasets"
    try:
        _api_request("POST", url, {"name": name, "description": description}, headers)
        print(f"created dataset: {name}")
    except RuntimeError as err:
        if "409" in str(err) or "already exists" in str(err).lower():
            print(f"dataset exists: {name}")
        else:
            raise


def upsert_item(host: str, headers: dict[str, str], dataset_name: str, payload: dict) -> None:
    url = f"{host.rstrip('/')}/api/public/dataset-items"
    body = {
        "datasetName": dataset_name,
        "id": payload["id"],
        "input": payload["input"],
        "expectedOutput": payload["expectedOutput"],
        "metadata": payload.get("metadata", {}),
    }
    _api_request("POST", url, body, headers)


def sync_manifest(
    path: Path,
    *,
    host: str,
    headers: dict[str, str],
    validate_only: bool,
    require_reviewed_by: bool,
    min_items: int,
) -> int:
    manifest = load_manifest(path)
    validate_manifest(
        manifest,
        manifest_path=path,
        require_reviewed_by=require_reviewed_by,
        min_items=min_items,
    )
    if validate_only:
        print(f"validate ok: {path} ({len(manifest.items)} items)")
        return 0

    dataset_name = langfuse_dataset_name(manifest)
    ensure_dataset(host, headers, dataset_name, manifest.description)
    for item in manifest.items:
        payload = manifest_to_langfuse_item(manifest, item)
        upsert_item(host, headers, dataset_name, payload)
    print(f"sync ok: {len(manifest.items)} items -> {dataset_name}")
    return len(manifest.items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync eval datasets to Langfuse")
    parser.add_argument("--dataset", default="all", help="group/name path or all")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--allow-unreviewed",
        action="store_true",
        help="skip reviewed_by gate (draft manifests only)",
    )
    parser.add_argument("--min-items", type=int, default=20)
    args = parser.parse_args()

    paths = discover_manifests(None if args.dataset == "all" else args.dataset)
    if not paths:
        print("sync_datasets: no manifests found")
        return 0

    require_reviewed_by = not args.allow_unreviewed
    for path in paths:
        min_items = args.min_items if "e2e-qa" in str(path) else 1
        if args.validate_only:
            sync_manifest(
                path,
                host="",
                headers={},
                validate_only=True,
                require_reviewed_by=require_reviewed_by,
                min_items=min_items,
            )
            continue

        _load_env()
        try:
            host, public_key, secret_key = resolve_langfuse_keys()
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            return 1
        headers = _auth_headers(public_key, secret_key)
        auth_check(host, public_key, secret_key)
        sync_manifest(
            path,
            host=host,
            headers=headers,
            validate_only=False,
            require_reviewed_by=require_reviewed_by,
            min_items=min_items,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
