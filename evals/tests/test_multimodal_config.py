"""Tests for multimodal eval config loader (sprint-07 task 03)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from env_loader import load_repo_env
from multimodal_config import MultimodalEvalConfig


def test_baseline_config_has_indexer_and_vector_db() -> None:
    load_repo_env()
    path = REPO_ROOT / "evals" / "configs" / "multimodal-baseline.yaml"
    cfg = MultimodalEvalConfig.from_yaml_path(path)
    assert cfg.config_id == "multimodal-baseline"
    assert cfg.indexer.method == "baseline"
    assert cfg.indexer.corpus_dir == "data/multimodal-rag/corpus/text_naive"
    assert cfg.vector_db.collection == "multimodal_baseline"


def test_stub_config_methods() -> None:
    load_repo_env()
    cases = {
        "multimodal-a-ocr-tesseract.yaml": "A_ocr_tesseract",
        "multimodal-c-unified.yaml": "C_unified",
        "multimodal-d-jina-multivector.yaml": "D_jina_multivector",
    }
    for filename, method in cases.items():
        path = REPO_ROOT / "evals" / "configs" / filename
        cfg = MultimodalEvalConfig.from_yaml_path(path)
        assert cfg.indexer.method == method
        assert cfg.indexer.corpus_dir


def test_make_indexer_registry_switch() -> None:
    from app.rag.indexers import make_indexer
    from app.rag.indexers.a_ocr_modern import ModernOcrIndexer

    assert isinstance(make_indexer("A_ocr_modern"), ModernOcrIndexer)


def test_resolve_corpus_dir_relative() -> None:
    load_repo_env()
    path = REPO_ROOT / "evals" / "configs" / "multimodal-baseline.yaml"
    cfg = MultimodalEvalConfig.from_yaml_path(path)
    resolved = cfg.resolve_corpus_dir(REPO_ROOT)
    assert resolved == (REPO_ROOT / "data" / "multimodal-rag" / "corpus" / "text_naive").resolve()
