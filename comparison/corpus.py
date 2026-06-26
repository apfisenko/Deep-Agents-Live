"""Загрузка учебного корпуса и его эмбеддинг через API (с кэшем на диск).

Один источник правды по данным для всего notebook. Когда появится реальный корпус
курса — меняется только тело load_texts(), интерфейс остаётся прежним:
тексты + категории (метаданные) + нормированные векторы.

Корпус по умолчанию — DBpedia-14: короткие энциклопедические аннотации, размеченные
по 14 классам (Company, Artist, Film, Animal, ...). Метка класса служит метаданными,
на которых мы показываем фильтрацию.

Эмбеддинги считаем моделью **intfloat/multilingual-e5-large** (1024-dim, 90+ языков)
через OpenRouter — это быстро (батчи + параллельные запросы) и не требует качать модель.
Нужен ключ OPENROUTER_API_KEY (положи в окружение или в .env рядом). Стоит копейки
($0.01 / 1M токенов). Результат кэшируется в embeddings_cache/*.npy — считается один раз.

Предсчитать заранее из терминала:
    python corpus.py 40000
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

EMBED_MODEL = "intfloat/multilingual-e5-large"  # 1024-dim, RU/EN/+90 языков (та же модель, что в уроке)
EMBED_DIM = 1024
SEED = 7
CACHE_DIR = Path(__file__).parent / "embeddings_cache"
API_URL = "https://openrouter.ai/api/v1/embeddings"

# e5 требует префиксы: документы — "passage: ", запросы — "query: " (см. урок, §4.2)
DOC_PREFIX = "passage: "
QUERY_PREFIX = "query: "


# --- Данные -----------------------------------------------------------------

def load_texts(n: int, seed: int = SEED):
    """Берёт n записей из DBpedia-14 (детерминированная подвыборка).

    Память-бережно: датасет лежит memory-mapped (Arrow), в RAM поднимаем только n строк.
    Возвращает (texts, categories): списки длины n.
    """
    from datasets import load_dataset

    ds = load_dataset("fancyzhx/dbpedia_14", split="train")
    class_names = ds.features["label"].names

    rng = np.random.default_rng(seed)
    idx = np.sort(rng.permutation(len(ds))[:n])  # sort — последовательное чтение memmap
    rows = ds.select(idx.tolist())

    texts = [r.strip() for r in rows["content"]]
    categories = [class_names[l] for l in rows["label"]]
    return texts, categories


# --- Эмбеддинг через API ----------------------------------------------------

def _api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        # пробуем подхватить из .env рядом или из корня репозитория
        for env_path in (Path(__file__).parent / ".env", Path(__file__).resolve().parents[1] / ".env"):
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith("OPENROUTER_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            if key:
                break
    if not key:
        raise RuntimeError(
            "Нужен OPENROUTER_API_KEY (в окружении или .env). "
            "Возьми ключ на openrouter.ai и положи в .env рядом с notebook."
        )
    return key


def _embed_batch(client, batch: list[str]) -> list[list[float]]:
    resp = client.post(
        API_URL,
        headers={"Authorization": f"Bearer {_KEY}"},
        json={"model": EMBED_MODEL, "input": batch},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()["data"]
    return [d["embedding"] for d in sorted(data, key=lambda d: d["index"])]


_KEY = None


def _embed(texts: list[str], prefix: str, *, batch_size: int = 64, workers: int = 12) -> np.ndarray:
    """Эмбеддит тексты через OpenRouter, L2-нормирует. Параллельно по батчам."""
    global _KEY
    _KEY = _api_key()
    import httpx

    inputs = [prefix + t for t in texts]
    batches = [inputs[i:i + batch_size] for i in range(0, len(inputs), batch_size)]

    with httpx.Client(http2=False) as client:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda b: _embed_batch(client, b), batches))

    vecs = np.asarray([v for batch in results for v in batch], dtype=np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12  # косинус = скалярное произв.
    return vecs


def embed_query(text: str) -> np.ndarray:
    """Эмбеддинг одного запроса (нормированный), с query-префиксом e5."""
    return _embed([text], QUERY_PREFIX, workers=1)[0]


# --- Кэш и сборка ------------------------------------------------------------

def _cache_file(n: int, seed: int) -> Path:
    return CACHE_DIR / f"dbpedia_{n}_{seed}.npy"


def precompute(n: int, seed: int = SEED) -> Path:
    """Считает и кэширует эмбеддинги документов для n записей. Идемпотентно."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache = _cache_file(n, seed)
    if cache.exists():
        print(f"кэш уже есть: {cache.name}")
        return cache
    print(f"эмбеддим {n} записей через {EMBED_MODEL} (один раз, потом из кэша)...")
    texts, _ = load_texts(n, seed=seed)
    vecs = _embed(texts, DOC_PREFIX)
    np.save(cache, vecs)
    print(f"готово: {cache.name} {vecs.shape}")
    return cache


def load_corpus(n: int, seed: int = SEED):
    """Тексты + категории + нормированные векторы (n, 1024). Эмбеддинги — из кэша.

    Если кэша нет — считает через API (лучше предсчитать `python corpus.py N`).
    """
    texts, categories = load_texts(n, seed=seed)
    cache = _cache_file(n, seed)
    if cache.exists():
        vectors = np.load(cache)
    else:
        CACHE_DIR.mkdir(exist_ok=True)
        vectors = _embed(texts, DOC_PREFIX)
        np.save(cache, vectors)
    return texts, categories, vectors[:n]


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40_000
    precompute(n)
