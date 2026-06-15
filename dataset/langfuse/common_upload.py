#!/usr/bin/env python3
"""Shared helpers to sync items.jsonl into a Langfuse dataset."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from base64 import b64encode
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"
SOURCE_JSONL = REPO_ROOT / "dataset" / "v0.1.jsonl"

TYPE_CONFIG = {
    "a": {
        "dataset_type": "faq-format",
        "dataset_name": "llmstart-type-a-v0.1",
        "description": "LLMStart agent eval: type A (faq-format), version v0.1",
    },
    "b": {
        "dataset_type": "product-fit",
        "dataset_name": "llmstart-type-b-v0.1",
        "description": "LLMStart agent eval: type B (product-fit), version v0.1",
    },
    "c": {
        "dataset_type": "segment-route",
        "dataset_name": "llmstart-type-c-v0.1",
        "description": "LLMStart agent eval: type C (segment-route), version v0.1",
    },
}


def load_env(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def api_request(
    method: str,
    url: str,
    body: dict | None,
    public_key: str,
    secret_key: str,
) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Basic "
            + b64encode(f"{public_key}:{secret_key}".encode()).decode(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} -> {exc.code}: {detail}") from exc


def export_items(dataset_type: str, out_path: Path) -> int:
    rows: list[dict] = []
    for line in SOURCE_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("metadata", {}).get("dataset_type") == dataset_type:
            rows.append(row)
    out_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    return len(rows)


def ensure_dataset(
    host: str,
    public_key: str,
    secret_key: str,
    dataset_name: str,
    description: str,
) -> None:
    url = f"{host.rstrip('/')}/api/public/v2/datasets"
    try:
        api_request(
            "POST",
            url,
            {"name": dataset_name, "description": description},
            public_key,
            secret_key,
        )
        print(f"created dataset: {dataset_name}")
    except RuntimeError as err:
        if "409" in str(err) or "already exists" in str(err).lower():
            print(f"dataset exists: {dataset_name}")
        else:
            raise


def upload_items_file(
    host: str,
    public_key: str,
    secret_key: str,
    dataset_name: str,
    items_file: Path,
) -> int:
    base = f"{host.rstrip('/')}/api/public/dataset-items"
    count = 0
    for line in items_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        payload = {
            "datasetName": dataset_name,
            "id": row["id"],
            "input": row["input"],
            "expectedOutput": row["expected_output"],
            "metadata": row.get("metadata", {}),
        }
        api_request("POST", base, payload, public_key, secret_key)
        count += 1
        print(f"  upserted {row['id']}")
    return count


def sync_type(type_key: str, folder: Path) -> int:
    cfg = TYPE_CONFIG[type_key]
    items_file = folder / "items.jsonl"
    n = export_items(cfg["dataset_type"], items_file)
    print(f"exported {n} items -> {items_file.name}")

    load_env()
    host = os.environ.get("LANGFUSE_HOST", "").rstrip("/")
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")
    if not all([host, public_key, secret_key]):
        raise RuntimeError("LANGFUSE_* missing in .env")

    ensure_dataset(host, public_key, secret_key, cfg["dataset_name"], cfg["description"])
    uploaded = upload_items_file(host, public_key, secret_key, cfg["dataset_name"], items_file)
    print(f"done: {uploaded} items -> {cfg['dataset_name']} @ {host}")
    return uploaded
