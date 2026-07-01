"""RunConfig retriever section validation."""

from app.agent.run_config import RunConfig
from app.paths import EVALS_CONFIGS_DIR


def test_graphrag_v001_config_loads() -> None:
    path = EVALS_CONFIGS_DIR / "graphrag-v001.yaml"
    config = RunConfig.from_yaml_path(path)
    assert config.config_id == "graphrag-v001"
    assert config.retriever.backend == "hybrid"
    assert config.retriever.reranker_model == "BAAI/bge-reranker-v2-m3"
    assert config.retriever.hybrid_weights.graph == 1.2


def test_graphrag_baseline_defaults_vector_retriever() -> None:
    path = EVALS_CONFIGS_DIR / "graphrag-baseline.yaml"
    config = RunConfig.from_yaml_path(path)
    assert config.retriever.backend == "vector"
