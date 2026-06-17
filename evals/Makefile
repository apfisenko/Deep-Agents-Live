# Eval contour Makefile (E-2)

CONFIG  ?= configs/baseline-react-inmemory.yaml
DATASET ?= e2e/e2e-qa
RUN     ?=
RUN_A   ?=
RUN_B   ?=

.PHONY: help validate build sync experiment analyze compare

help:
	@echo "Eval contour — полный цикл v0.2:"
	@echo ""
	@echo "  1. build      — собрать YAML-манифест из исходников"
	@echo "  2. validate   — проверить манифесты и конфиги"
	@echo "  3. sync       — загрузить датасет(ы) в Langfuse"
	@echo "  4. experiment — прогнать эксперимент (agent + judge evaluators)"
	@echo "  5. analyze    — error analysis по run"
	@echo "  6. compare    — сравнить baseline vs candidate (E-16/E-18)"
	@echo ""
	@echo "Targets:"
	@echo "  build      DATASET=e2e/e2e-qa|all"
	@echo "  validate   CONFIG=$(CONFIG)"
	@echo "  sync       DATASET=all|e2e/e2e-qa|..."
	@echo "  experiment CONFIG=$(CONFIG) DATASET=$(DATASET)"
	@echo "  analyze    RUN=<run-name> EMIT_ITEMS=1 (optional K-4 emit)"
	@echo "  compare    RUN_A=<baseline> RUN_B=<candidate>"
	@echo ""
	@echo "Env (.env): LLM_MODEL, LLM_TEMPERATURE, EMBEDDING_MODEL,"
	@echo "  EVAL_JUDGE_MODEL, EVAL_JUDGE_TEMPERATURE, EVAL_DATASET_NAME,"
	@echo "  EVAL_DATASET_PREFIX, LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY"

validate:
	uv run pytest tests/ -q
	uv run python scripts/run_experiment.py --config $(CONFIG) --dataset all --dry-run

build:
	uv run python scripts/build_dataset.py --dataset $(DATASET)

sync: validate
	uv run python scripts/sync_datasets.py --dataset $(DATASET)

experiment: sync
	uv run python scripts/run_experiment.py --config $(CONFIG) --dataset $(DATASET)

analyze:
	uv run python scripts/analyze_run.py --run "$(RUN)" --out reports/ $(if $(EMIT_ITEMS),--emit-items,)

compare:
	uv run python scripts/compare_runs.py --a "$(RUN_A)" --b "$(RUN_B)" --out reports/
