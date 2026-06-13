"""Upload or reload a validation dataset JSONL into Langfuse."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSONL = REPO_ROOT / "datasets" / "dataset-v1.jsonl"
DEFAULT_DATASET_NAME = "llmstart-agent-v1"


class LangfuseApiError(RuntimeError):
    """Langfuse HTTP API error."""


class LangfuseRestClient:
    def __init__(self, *, host: str, public_key: str, secret_key: str, timeout_sec: float) -> None:
        token = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        self._host = host.rstrip("/")
        self._client = httpx.Client(
            base_url=self._host,
            timeout=timeout_sec,
            headers={"Authorization": f"Basic {token}"},
        )

    def close(self) -> None:
        self._client.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self._client.request(method, path, **kwargs)
            except httpx.HTTPError as exc:
                last_error = exc
                time.sleep(2)
                continue
            if response.status_code >= 400:
                raise LangfuseApiError(
                    f"{method} {path} -> {response.status_code}: {response.text}",
                )
            if not response.content:
                return None
            return response.json()
        if last_error is not None:
            raise LangfuseApiError(f"{method} {path} failed: {last_error}") from last_error
        raise LangfuseApiError(f"{method} {path} failed after retries")

    def ensure_dataset(self, *, name: str, description: str) -> dict[str, Any]:
        listed = self._request(
            "GET",
            "/api/public/v2/datasets",
            params={"name": name, "page": 1, "limit": 1},
        )
        data = listed.get("data", [])
        if data:
            return data[0]
        return self._request(
            "POST",
            "/api/public/v2/datasets",
            json={"name": name, "description": description},
        )

    def list_item_ids(self, dataset_name: str) -> list[str]:
        ids: list[str] = []
        page = 1
        while True:
            payload = self._request(
                "GET",
                "/api/public/dataset-items",
                params={"datasetName": dataset_name, "page": page, "limit": 100},
            )
            data = payload.get("data", [])
            ids.extend(item["id"] for item in data if item.get("id"))
            meta = payload.get("meta", {})
            if page >= meta.get("totalPages", 1):
                break
            page += 1
        return ids

    def delete_item(self, item_id: str) -> None:
        self._request("DELETE", f"/api/public/dataset-items/{item_id}")

    def upsert_item(
        self,
        *,
        dataset_name: str,
        item_id: str,
        input_value: Any,
        expected_output: Any,
        metadata: Any,
    ) -> None:
        self._request(
            "POST",
            "/api/public/dataset-items",
            json={
                "id": item_id,
                "datasetName": dataset_name,
                "input": input_value,
                "expectedOutput": expected_output,
                "metadata": metadata,
            },
        )


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"FAIL: missing env {name}", file=sys.stderr)
        raise SystemExit(1)
    return value


def _health_ok(host: str, timeout_sec: float = 5.0) -> bool:
    try:
        with httpx.Client(timeout=timeout_sec) as client:
            response = client.get(f"{host.rstrip('/')}/api/public/health")
            return response.status_code == 200
    except httpx.HTTPError:
        return False


def _wsl_fallback_host(port: int = 3001) -> str | None:
    if os.name != "nt" or not shutil.which("wsl"):
        return None
    try:
        proc = subprocess.run(
            ["wsl", "hostname", "-I"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    for ip in proc.stdout.strip().split():
        candidate = f"http://{ip}:{port}"
        if _health_ok(candidate):
            return candidate
    return None


def _resolve_langfuse_host(preferred: str) -> str:
    preferred = preferred.rstrip("/")
    if _health_ok(preferred):
        return preferred
    fallback = _wsl_fallback_host()
    if fallback:
        print(f"info: using WSL Langfuse host {fallback}")
        return fallback
    return preferred


def _wait_for_health(host: str, timeout_sec: float) -> None:
    url = f"{host.rstrip('/')}/api/public/health"
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if _health_ok(host):
            return
        time.sleep(2)
    print(f"FAIL: Langfuse not reachable at {url}", file=sys.stderr)
    raise SystemExit(1)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"FAIL: invalid JSON at {path}:{line_no}: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
    return records


def _stable_item_id(dataset_name: str, index: int, record: dict[str, Any]) -> str:
    meta = record.get("metadata") or {}
    parts = [
        dataset_name,
        str(index),
        str(meta.get("synthetic_id", "")),
        str(meta.get("chat_id", "")),
        str(meta.get("user_msg_index", "")),
        str(meta.get("source", "")),
    ]
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]
    return f"{dataset_name}-{digest}"


def _dataset_ui_url(host: str, project_id: str, dataset_id: str) -> str:
    return f"{host.rstrip('/')}/project/{project_id}/datasets/{dataset_id}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload JSONL validation dataset to Langfuse")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_JSONL,
        help=f"JSONL file (default: {DEFAULT_JSONL})",
    )
    parser.add_argument(
        "--dataset-name",
        default=DEFAULT_DATASET_NAME,
        help=f"Langfuse dataset name (default: {DEFAULT_DATASET_NAME})",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Delete all existing dataset items before upload",
    )
    parser.add_argument(
        "--wait-sec",
        type=float,
        default=float(os.getenv("LANGFUSE_UPLOAD_WAIT_SEC", "120")),
        help="Seconds to wait for Langfuse health before upload",
    )
    args = parser.parse_args()

    _load_dotenv()
    public_key = _require_env("LANGFUSE_PUBLIC_KEY")
    secret_key = _require_env("LANGFUSE_SECRET_KEY")
    host = _resolve_langfuse_host(os.getenv("LANGFUSE_HOST", "http://localhost:3001").strip())
    timeout_sec = float(os.getenv("LANGFUSE_REQUEST_TIMEOUT_SEC", "30"))

    if not args.input.is_file():
        print(f"FAIL: file not found: {args.input}", file=sys.stderr)
        raise SystemExit(1)

    records = _read_jsonl(args.input)
    if not records:
        print("FAIL: JSONL has no records", file=sys.stderr)
        raise SystemExit(1)

    _wait_for_health(host, args.wait_sec)

    description = f"Validation dataset uploaded from {args.input.name} ({len(records)} records)"

    deleted = 0
    uploaded = 0
    dataset_id = ""
    project_id = ""

    client = LangfuseRestClient(
        host=host,
        public_key=public_key,
        secret_key=secret_key,
        timeout_sec=timeout_sec,
    )
    try:
        dataset = client.ensure_dataset(name=args.dataset_name, description=description)
        dataset_id = dataset.get("id", "")
        project_id = dataset.get("projectId") or dataset.get("project_id", "")

        if args.reload:
            for item_id in client.list_item_ids(args.dataset_name):
                client.delete_item(item_id)
                deleted += 1

        for index, record in enumerate(records, start=1):
            if "input" not in record:
                print(f"FAIL: record {index} missing 'input'", file=sys.stderr)
                raise SystemExit(1)
            client.upsert_item(
                dataset_name=args.dataset_name,
                item_id=_stable_item_id(args.dataset_name, index, record),
                input_value=record["input"],
                expected_output=record.get("expected_output"),
                metadata=record.get("metadata"),
            )
            uploaded += 1
    finally:
        client.close()

    ui_url = (
        _dataset_ui_url(host, project_id, dataset_id)
        if project_id and dataset_id
        else f"{host}/datasets"
    )

    print(f"dataset_name: {args.dataset_name}")
    print(f"dataset_id: {dataset_id}")
    print(f"source_file: {args.input}")
    print(f"records_in_file: {len(records)}")
    print(f"items_deleted: {deleted}")
    print(f"items_uploaded: {uploaded}")
    print(f"langfuse_ui: {ui_url}")


if __name__ == "__main__":
    main()
