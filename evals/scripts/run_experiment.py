"""Run Langfuse experiment against Agent Core (E-3, E-6, E-9)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from langfuse import Langfuse

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.agent.prompt_resolver import resolve_prompt
from app.agent.run_config import RunConfig
from dataset_registry import (
    ALL_DATASET_SLUGS,
    DatasetTarget,
    resolve_all_dataset_targets,
    resolve_dataset_target,
    slug_to_run_suffix,
)
from env_loader import load_repo_env, resolve_langfuse_keys
from evaluators import (
    build_judge_runtime,
    evaluator_names_for_slug,
    judge_metadata,
    make_item_evaluators,
    make_run_evaluators,
)
from models import load_manifest

EVALS_ROOT = REPO_ROOT / "evals"
SEARCH_TOOL_NAMES = frozenset({"search_knowledge_base_tool", "search_knowledge_base"})
FUNNEL_SLUG = "behavior/funnel-to-lead"


@dataclass(frozen=True)
class AgentCallResult:
    answer: str = ""
    contexts: list[str] = field(default_factory=list)
    tools_called: list[str] = field(default_factory=list)


def resolve_eval_stream_url(api_url: str) -> str:
    """Eval always uses SSE so retrieved KB chunks can be captured for faithfulness."""
    base = api_url.rstrip("/")
    if base.endswith("/chat/stream"):
        return base
    if base.endswith("/chat"):
        return base.replace("/chat", "/chat/stream")
    return f"{base}/chat/stream"


def extract_contexts_from_tool_result(tool_name: str, result: Any) -> list[str]:
    if tool_name not in SEARCH_TOOL_NAMES:
        return []
    payload: Any = result
    if isinstance(result, str):
        try:
            payload = json.loads(result)
        except json.JSONDecodeError:
            return [result] if result.strip() else []
    if isinstance(payload, dict) and "error" in payload:
        return []
    if not isinstance(payload, list):
        return [str(payload)] if payload else []
    contexts: list[str] = []
    for item in payload:
        if isinstance(item, dict):
            text = item.get("text")
            if text:
                contexts.append(str(text))
        elif item:
            contexts.append(str(item))
    return contexts


def parse_sse_event(current_event: str | None, data: dict[str, Any]) -> AgentCallResult | None:
    if current_event == "token" and "text" in data:
        return AgentCallResult(answer=str(data["text"]))
    if current_event == "tool_call" and "name" in data:
        return AgentCallResult(tools_called=[str(data["name"])])
    if current_event == "tool_result":
        tool_name = str(data.get("name", ""))
        contexts = extract_contexts_from_tool_result(tool_name, data.get("result"))
        if contexts:
            return AgentCallResult(contexts=contexts)
    return None


def merge_agent_call_results(parts: list[AgentCallResult]) -> AgentCallResult:
    answer = "".join(part.answer for part in parts).strip()
    contexts: list[str] = []
    seen: set[str] = set()
    tools_called: list[str] = []
    for part in parts:
        tools_called.extend(part.tools_called)
        for context in part.contexts:
            if context not in seen:
                seen.add(context)
                contexts.append(context)
    return AgentCallResult(answer=answer, contexts=contexts, tools_called=tools_called)


def _load_env() -> None:
    load_repo_env()


def git_sha8() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=8", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def iso_ts() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def run_name(config: RunConfig, dataset_slug: str) -> str:
    suffix = slug_to_run_suffix(dataset_slug)
    return f"{config.config_id}--{suffix}--{git_sha8()}--{iso_ts()}"


def build_run_metadata(
    config: RunConfig,
    *,
    target: DatasetTarget,
    config_path: Path,
    simulation_mode: str = "isolated",
) -> dict[str, str]:
    prompt_text = resolve_prompt(config.prompt)
    return {
        "config_id": config.config_id,
        "config_path": str(config_path.relative_to(REPO_ROOT)),
        "git_sha": git_sha8(),
        "dataset_name": target.full_name,
        "dataset_slug": target.slug,
        "dataset_version": target.version,
        "manifest_path": str(target.manifest_path.relative_to(REPO_ROOT)),
        "simulation_mode": simulation_mode,
        "evaluator_profile": ",".join(
            evaluator_names_for_slug(
                target.slug,
                simulation=simulation_mode == "multi_turn",
            ),
        ),
        "prompt_source": config.prompt.source,
        "prompt_name": config.prompt.name,
        "prompt_path": config.prompt.path or "",
        "prompt_resolved_preview": prompt_text[:200],
        "agent_api_url": config.agent.api_url,
        "model_name": config.model.name,
        "model_temperature": str(config.model.temperature),
        "retrieval_backend": config.retrieval.backend,
        **judge_metadata(config.judge),
    }


def check_backend(api_url: str, *, min_rag_docs: int = 1) -> None:
    health_url = api_url.replace("/api/v1/chat", "/health")
    reindex_url = api_url.replace("/api/v1/chat", "/admin/reindex")
    with httpx.Client(timeout=120.0) as client:
        reindex_resp = client.post(reindex_url)
        if reindex_resp.status_code not in (200, 404):
            reindex_resp.raise_for_status()
        response = client.get(health_url)
        response.raise_for_status()
        rag_docs = int(response.json().get("rag_indexed_docs", 0))
        if rag_docs < min_rag_docs:
            msg = (
                f"RAG index empty (rag_indexed_docs={rag_docs}); "
                "start backend with ENV=dev for /admin/reindex"
            )
            raise RuntimeError(msg)


def check_langfuse(host: str, public_key: str, secret_key: str) -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{host.rstrip('/')}/api/public/health")
        response.raise_for_status()
    Langfuse(public_key=public_key, secret_key=secret_key, host=host).auth_check()


async def call_agent(
    client: httpx.AsyncClient,
    *,
    url: str,
    payload: dict[str, Any],
) -> AgentCallResult:
    if url.endswith("/chat/stream"):
        parts: list[AgentCallResult] = []
        current_event: str | None = None
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    current_event = line.removeprefix("event:").strip()
                    continue
                if not line.startswith("data:"):
                    continue
                data = json.loads(line.removeprefix("data:").strip())
                parsed = parse_sse_event(current_event, data)
                if parsed is not None:
                    parts.append(parsed)
        return merge_agent_call_results(parts)

    response = await client.post(url, json=payload)
    response.raise_for_status()
    body = response.json()
    return AgentCallResult(answer=str(body.get("reply", "")).strip())


def make_task(config: RunConfig) -> Any:
    async def task(*, item: Any, **_kw: Any) -> dict[str, Any]:
        input_data = item.input if hasattr(item, "input") else item["input"]
        message = input_data["message"]
        channel = input_data.get("channel", "web")
        session_id = str(uuid4())
        started = time.perf_counter()

        item_id = None
        if isinstance(item, dict):
            meta = item.get("metadata") or {}
            item_id = meta.get("item_id")
        elif hasattr(item, "metadata"):
            meta = item.metadata or {}
            item_id = meta.get("item_id") if isinstance(meta, dict) else getattr(item, "id", None)

        payload = {
            "session_id": session_id,
            "channel": "web",
            "message": message,
            "config_id": config.config_id,
            "metadata": {
                "eval_item_id": item_id,
                "eval_source_channel": channel,
            },
        }

        chat_url = resolve_eval_stream_url(config.agent.api_url)
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                result = await call_agent(client, url=chat_url, payload=payload)
        except Exception as exc:
            return {
                "answer": "",
                "contexts": [],
                "tools_called": [],
                "session_id": session_id,
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "error": str(exc),
            }

        return {
            "answer": result.answer,
            "contexts": result.contexts,
            "tools_called": result.tools_called,
            "session_id": session_id,
            "duration_ms": int((time.perf_counter() - started) * 1000),
            "error": None if result.answer else "empty reply",
        }

    return task


def scenarios_path_for_target(target: DatasetTarget) -> Path:
    return target.manifest_path.parent / "scenarios.yaml"


def should_use_simulation(target: DatasetTarget, *, isolated: bool) -> bool:
    if isolated or target.slug != FUNNEL_SLUG:
        return False
    return scenarios_path_for_target(target).exists()


def resolve_experiment_items(
    target: DatasetTarget,
    *,
    limit: int,
    isolated: bool,
) -> tuple[list[dict[str, Any]], str]:
    if should_use_simulation(target, isolated=isolated):
        from user_simulation import load_scenarios, scenarios_to_experiment_items

        scenarios = load_scenarios(scenarios_path_for_target(target))
        items = scenarios_to_experiment_items(scenarios)
        mode = "multi_turn"
    else:
        items = manifest_to_experiment_items(target.manifest_path)
        mode = "isolated"
    if limit > 0:
        items = items[:limit]
    return items, mode


def make_simulation_task(config: RunConfig, scenarios_path: Path) -> Any:
    from user_simulation import load_scenarios, run_scenario

    scenarios = load_scenarios(scenarios_path)
    scenario_map = {scenario.id: scenario for scenario in scenarios.scenarios}

    async def task(*, item: Any, **_kw: Any) -> dict[str, Any]:
        input_data = item.input if hasattr(item, "input") else item["input"]
        scenario_id = str(input_data.get("scenario_id", ""))
        scenario = scenario_map.get(scenario_id)
        if scenario is None:
            return {
                "answer": "",
                "contexts": [],
                "tools_called": [],
                "session_id": "",
                "duration_ms": 0,
                "error": f"unknown scenario_id={scenario_id}",
            }

        chat_url = resolve_eval_stream_url(config.agent.api_url)
        async with httpx.AsyncClient(timeout=300.0) as client:
            return await run_scenario(
                client,
                chat_url=chat_url,
                config_id=config.config_id,
                scenario=scenario,
            )

    return task


def manifest_to_experiment_items(manifest_path: Path) -> list[dict[str, Any]]:
    manifest = load_manifest(manifest_path)
    items: list[dict[str, Any]] = []
    for item in manifest.items:
        meta = item.metadata.model_dump(exclude_none=True)
        facts = meta.pop("facts", item.metadata.facts)
        metadata = {
            **meta,
            "item_id": item.id,
            "facts_count": len(facts),
        }
        if facts:
            preview = "; ".join(facts[:3])
            metadata["facts_preview"] = preview[:200]
        expected_output = item.expected_output.model_dump()
        expected_output["reference_facts"] = facts
        items.append(
            {
                "input": item.input.model_dump(),
                "expected_output": expected_output,
                "metadata": metadata,
            },
        )
    return items


def dry_run(config_path: Path, dataset_arg: str, *, isolated: bool = False) -> int:
    config = RunConfig.from_yaml_path(config_path)
    if dataset_arg == "all":
        targets = resolve_all_dataset_targets(config)
        for target in targets:
            items, mode = resolve_experiment_items(target, limit=0, isolated=isolated)
            metadata = build_run_metadata(
                config,
                target=target,
                config_path=config_path,
                simulation_mode=mode,
            )
            name = run_name(config, target.slug)
            evaluators = evaluator_names_for_slug(
                target.slug,
                simulation=mode == "multi_turn",
            )
            print(f"dry-run ok: run_name={name}")
            print(f"dataset={target.full_name}")
            print(f"items={len(items)} mode={mode}")
            print(f"evaluators={','.join(evaluators)}")
            print(f"metadata keys={sorted(metadata.keys())}")
        return 0

    target = resolve_dataset_target(config, dataset_arg)
    items, mode = resolve_experiment_items(target, limit=0, isolated=isolated)
    metadata = build_run_metadata(
        config,
        target=target,
        config_path=config_path,
        simulation_mode=mode,
    )
    name = run_name(config, target.slug)
    evaluators = evaluator_names_for_slug(target.slug, simulation=mode == "multi_turn")
    print(f"dry-run ok: run_name={name}")
    print(f"dataset={target.full_name}")
    print(f"items={len(items)} mode={mode}")
    print(f"evaluators={','.join(evaluators)}")
    print(f"metadata keys={sorted(metadata.keys())}")
    return 0


def run_experiment_for_target(
    *,
    config: RunConfig,
    config_path: Path,
    target: DatasetTarget,
    langfuse: Langfuse,
    judge: Any,
    limit: int,
    isolated: bool = False,
) -> Path:
    items, mode = resolve_experiment_items(target, limit=limit, isolated=isolated)
    use_simulation = mode == "multi_turn"

    metadata = build_run_metadata(
        config,
        target=target,
        config_path=config_path,
        simulation_mode=mode,
    )
    experiment_run_name = run_name(config, target.slug)
    task = (
        make_simulation_task(config, scenarios_path_for_target(target))
        if use_simulation
        else make_task(config)
    )

    print(f"starting experiment: {experiment_run_name} ({len(items)} items, mode={mode})")
    result = langfuse.run_experiment(
        name=f"baseline-{target.full_name}",
        run_name=experiment_run_name,
        description=config.comment,
        data=items,
        task=task,
        evaluators=make_item_evaluators(
            judge,
            dataset_slug=target.slug,
            simulation=use_simulation,
        ),
        run_evaluators=make_run_evaluators(
            dataset_slug=target.slug,
            simulation=use_simulation,
        ),
        max_concurrency=1 if use_simulation else 2,
        metadata=metadata,
    )

    report_path = EVALS_ROOT / "reports" / f"{experiment_run_name}.txt"
    report_path.write_text(result.format(), encoding="utf-8")
    print(f"experiment complete: {experiment_run_name}")
    print(f"report: {report_path}")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run eval experiment")
    parser.add_argument("--config", required=True, help="Path to run config YAML")
    parser.add_argument(
        "--dataset",
        default="e2e/e2e-qa",
        help=f"Dataset slug or all. Supported: {', '.join(ALL_DATASET_SLUGS)}, all",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate config without API calls")
    parser.add_argument(
        "--isolated",
        action="store_true",
        help="Use manifest single-turn items (skip scenarios.yaml user simulation)",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit items (0 = all)")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = EVALS_ROOT / config_path

    if args.dry_run:
        _load_env()
        return dry_run(config_path, args.dataset, isolated=args.isolated)

    _load_env()
    config = RunConfig.from_yaml_path(config_path)

    try:
        host, public_key, secret_key = resolve_langfuse_keys()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    try:
        check_backend(config.agent.api_url)
        check_langfuse(host, public_key, secret_key)
    except Exception as exc:
        print(f"ERROR: prerequisite check failed: {exc}")
        return 1

    langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    judge = build_judge_runtime(config)

    if args.dataset == "all":
        for slug in ALL_DATASET_SLUGS:
            target = resolve_dataset_target(config, slug)
            run_experiment_for_target(
                config=config,
                config_path=config_path,
                target=target,
                langfuse=langfuse,
                judge=judge,
                limit=args.limit,
                isolated=args.isolated,
            )
    else:
        target = resolve_dataset_target(config, args.dataset)
        run_experiment_for_target(
            config=config,
            config_path=config_path,
            target=target,
            langfuse=langfuse,
            judge=judge,
            limit=args.limit,
            isolated=args.isolated,
        )

    langfuse.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
