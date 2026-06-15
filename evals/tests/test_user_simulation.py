"""User simulation (E-23) unit tests."""

from __future__ import annotations

import json
from pathlib import Path

from app.agent.run_config import RunConfig
from dataset_registry import resolve_dataset_target
from user_simulation import (
    load_scenarios,
    scenarios_to_experiment_items,
    task_completion_heuristic,
)

EVALS_ROOT = Path(__file__).resolve().parents[1]
CONFIG = EVALS_ROOT / "configs" / "baseline-react-inmemory.yaml"
SCENARIOS = EVALS_ROOT / "datasets" / "behavior" / "funnel-to-lead" / "scenarios.yaml"


def test_load_scenarios() -> None:
    scenarios = load_scenarios(SCENARIOS)
    assert scenarios.version == "v001"
    assert len(scenarios.scenarios) == 2
    assert scenarios.scenarios[0].id == "fnl-scn-full-001"


def test_scenarios_to_experiment_items() -> None:
    scenarios = load_scenarios(SCENARIOS)
    items = scenarios_to_experiment_items(scenarios)
    assert len(items) == 2
    assert items[0]["input"]["scenario_id"] == "fnl-scn-full-001"
    assert "save_lead" in items[0]["expected_output"]["expected_tools"]


def test_task_completion_heuristic_full() -> None:
    score = task_completion_heuristic(
        tools_called=[
            "list_b2c_products",
            "create_payment_link",
            "confirm_payment",
            "save_lead",
        ],
        expected_tools=[
            "list_b2c_products",
            "create_payment_link",
            "confirm_payment",
            "save_lead",
        ],
        lead_saved=True,
        payment_link_ok=True,
    )
    assert score == 1.0


def test_state_check_lead_reads_file(tmp_path: Path) -> None:
    from user_simulation import read_leads_for_session

    leads_file = tmp_path / "leads.txt"
    leads_file.write_text(
        json.dumps(
            {
                "session_id": "sess-123",
                "contact": "eval-fnl-scn-001@example.com",
                "product_id": "deep-agents",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    records = read_leads_for_session("sess-123", leads_path=leads_file)
    assert len(records) == 1
    assert "eval-fnl-scn-001@example.com" in records[0]["contact"]


def test_funnel_resolves_simulation_items() -> None:
    from run_experiment import resolve_experiment_items

    config = RunConfig.from_yaml_path(CONFIG)
    target = resolve_dataset_target(config, "behavior/funnel-to-lead")
    items, mode = resolve_experiment_items(target, limit=0, isolated=False)
    assert mode == "multi_turn"
    assert len(items) == 2
