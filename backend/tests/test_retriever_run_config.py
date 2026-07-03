"""RunConfig retriever section validation."""

from app.agent.run_config import RunConfig
from app.paths import EVALS_CONFIGS_DIR


def test_graphrag_v001_config_loads() -> None:
    path = EVALS_CONFIGS_DIR / "graphrag-v001.yaml"
    config = RunConfig.from_yaml_path(path)
    assert config.config_id == "graphrag-v001"
    assert config.retriever.backend == "hybrid"
    assert config.retriever.reranker_model == "jinaai/jina-reranker-v2-base-multilingual"
    assert config.retriever.hybrid_weights.graph == 1.2


def test_graphrag_baseline_defaults_vector_retriever() -> None:
    path = EVALS_CONFIGS_DIR / "graphrag-baseline.yaml"
    config = RunConfig.from_yaml_path(path)
    assert config.retriever.backend == "vector"


def test_graphrag_final_routing_config() -> None:
    path = EVALS_CONFIGS_DIR / "graphrag-final.yaml"
    config = RunConfig.from_yaml_path(path)
    assert config.config_id == "graphrag-final"
    assert config.agent.routing_enabled is True
    assert config.retriever.backend == "vector"
    assert config.prompt.name == "SYSTEM_PROMPT_GRAPHRAG_ROUTING"
    assert "executed_tools_count" in config.extra_evaluators


def test_to_metadata_values_are_strings() -> None:
    path = EVALS_CONFIGS_DIR / "graphrag-v001.yaml"
    config = RunConfig.from_yaml_path(path)
    metadata = config.to_metadata()
    assert all(isinstance(value, str) for value in metadata.values())
    assert metadata["benchmark_only"] in {"true", "false"}
