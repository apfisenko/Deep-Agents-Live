"""Multi-turn user simulation for behavior datasets (E-23)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import yaml
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings

DEFAULT_SCENARIOS = (
    REPO_ROOT / "evals" / "datasets" / "behavior" / "funnel-to-lead" / "scenarios.yaml"
)


class ScenarioSuccess(BaseModel):
    expected_tools_in_order: list[str] = Field(min_length=1)
    lead_contact: str = Field(min_length=3)
    require_payment_link: bool = True


class ScenarioTurn(BaseModel):
    message: str = Field(min_length=1)


class UserScenario(BaseModel):
    id: str = Field(min_length=1)
    description: str = ""
    channel: str = "web"
    turns: list[ScenarioTurn] = Field(min_length=1)
    success: ScenarioSuccess


class ScenariosFile(BaseModel):
    version: str
    created: str
    description: str = ""
    scenarios: list[UserScenario] = Field(min_length=1)


def load_scenarios(path: Path | None = None) -> ScenariosFile:
    scenarios_path = path or DEFAULT_SCENARIOS
    raw = yaml.safe_load(scenarios_path.read_text(encoding="utf-8"))
    return ScenariosFile.model_validate(raw)


def scenarios_to_experiment_items(scenarios: ScenariosFile) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for scenario in scenarios.scenarios:
        items.append(
            {
                "input": {
                    "scenario_id": scenario.id,
                    "channel": scenario.channel,
                    "turn_count": len(scenario.turns),
                },
                "expected_output": {
                    "expected_tools": scenario.success.expected_tools_in_order,
                    "lead_contact": scenario.success.lead_contact,
                    "require_payment_link": scenario.success.require_payment_link,
                },
                "metadata": {
                    "item_id": scenario.id,
                    "simulation": True,
                    "description": scenario.description,
                },
            },
        )
    return items


def read_leads_for_session(session_id: str, *, leads_path: Path | None = None) -> list[dict[str, Any]]:
    path = leads_path or Path(get_settings().leads_path)
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("session_id") == session_id:
            records.append(row)
    return records


def state_check_lead(session_id: str, expected_contact: str) -> bool:
    records = read_leads_for_session(session_id)
    contact_lower = expected_contact.lower()
    return any(contact_lower in str(row.get("contact", "")).lower() for row in records)


def task_completion_heuristic(
    *,
    tools_called: list[str],
    expected_tools: list[str],
    lead_saved: bool,
    payment_link_ok: bool,
) -> float:
    if not expected_tools:
        return 1.0 if lead_saved else 0.0
    matched = 0
    idx = 0
    for tool in tools_called:
        if idx < len(expected_tools) and tool == expected_tools[idx]:
            idx += 1
            matched += 1
    tool_score = matched / len(expected_tools)
    if lead_saved and payment_link_ok and tool_score >= 1.0:
        return 1.0
    if lead_saved and tool_score >= 0.75:
        return 0.8
    return round(tool_score * 0.5, 3)


async def run_scenario(
    client: httpx.AsyncClient,
    *,
    chat_url: str,
    config_id: str,
    scenario: UserScenario,
) -> dict[str, Any]:
    from run_experiment import call_agent

    session_id = str(uuid4())
    started = time.perf_counter()
    all_tools: list[str] = []
    replies: list[str] = []
    channel = scenario.channel if scenario.channel in {"web", "telegram"} else "web"

    for turn in scenario.turns:
        payload = {
            "session_id": session_id,
            "channel": channel,
            "message": turn.message,
            "config_id": config_id,
            "metadata": {
                "eval_scenario_id": scenario.id,
                "simulation": True,
            },
        }
        try:
            result = await call_agent(client, url=chat_url, payload=payload)
        except Exception as exc:
            return {
                "answer": "\n---\n".join(replies),
                "contexts": [],
                "tools_called": all_tools,
                "session_id": session_id,
                "turns": len(replies),
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "error": str(exc),
            }
        all_tools.extend(result.tools_called)
        if result.answer:
            replies.append(result.answer)

    lead_saved = state_check_lead(session_id, scenario.success.lead_contact)
    payment_link_ok = "create_payment_link" in all_tools or not scenario.success.require_payment_link
    completion = task_completion_heuristic(
        tools_called=all_tools,
        expected_tools=scenario.success.expected_tools_in_order,
        lead_saved=lead_saved,
        payment_link_ok=payment_link_ok,
    )

    return {
        "answer": "\n---\n".join(replies),
        "contexts": [],
        "tools_called": all_tools,
        "session_id": session_id,
        "turns": len(scenario.turns),
        "lead_saved": lead_saved,
        "payment_link_ok": payment_link_ok,
        "task_completion": completion,
        "duration_ms": int((time.perf_counter() - started) * 1000),
        "error": None,
    }
