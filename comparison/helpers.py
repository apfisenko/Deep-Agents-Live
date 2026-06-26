"""Утилиты для notebook-сравнения векторных баз.

Здесь — только измерительная «сантехника», чтобы не зашумлять основной notebook:
тайминги, замер RAM, recall@k через точный перебор. Логика демонстраций — в notebook.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import time
from contextlib import contextmanager

import numpy as np


# --- Тайминги ---------------------------------------------------------------


@contextmanager
def timer(label: str = ""):
    """Контекст-менеджер: печатает, сколько заняло тело блока.

    with timer("индексация"):
        ...
    """
    t0 = time.perf_counter()
    yield (box := {})
    dt = time.perf_counter() - t0
    box["seconds"] = dt
    if label:
        print(f"{label}: {dt:.2f} c")


def throughput(fn, n_queries: int, *, warmup: int = 3) -> dict:
    """Гоняет fn() n_queries раз подряд, возвращает p50/p95 latency и QPS.

    fn — замыкание, делающее ОДИН поисковый запрос. Однопоточно (последовательно):
    нам важно сравнить базы в одинаковых условиях, а не выжать максимум из железа.
    """
    for _ in range(warmup):
        fn()
    lat = []
    t0 = time.perf_counter()
    for _ in range(n_queries):
        s = time.perf_counter()
        fn()
        lat.append((time.perf_counter() - s) * 1000)  # мс
    total = time.perf_counter() - t0
    lat = np.array(lat)
    return {
        "p50_ms": float(np.percentile(lat, 50)),
        "p95_ms": float(np.percentile(lat, 95)),
        "qps": n_queries / total,
    }


# --- Память -----------------------------------------------------------------


def _docker_stats_cmd() -> list[str]:
    """Команда `docker stats` с учётом Windows + Docker в WSL."""
    docker_args = [
        "docker",
        "stats",
        "--no-stream",
        "--format",
        "{{.Name}}\t{{.MemUsage}}",
    ]
    if platform.system() == "Windows" and shutil.which("docker") is None:
        if shutil.which("wsl") is None:
            raise RuntimeError(
                "docker не найден в PATH и wsl недоступен. "
                "На Windows подними базы через .\\make_u.ps1 up и установи WSL."
            )
        return ["wsl", "-e", *docker_args]
    return docker_args


def container_ram_mb(name_substring: str) -> float:
    """RAM контейнера (МиБ) по подстроке имени — через `docker stats --no-stream`.

    Так меряем серверные базы (Qdrant, pgvector) единообразно. Chroma работает
    embedded внутри процесса notebook — её память смотрим через RSS процесса
    (см. process_ram_mb), это честная асимметрия: разные модели развёртывания.
    """
    out = subprocess.run(
        _docker_stats_cmd(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for line in out.splitlines():
        if name_substring in line:
            usage = line.split("\t")[1].split("/")[0].strip()  # "58.09MiB"
            return _parse_mem(usage)
    raise RuntimeError(f"контейнер с '{name_substring}' не найден в docker stats")


def process_ram_mb() -> float:
    """ТЕКУЩИЙ RSS процесса (МиБ) — для embedded-Chroma.

    Читаем VmRSS из /proc/self/status (текущее потребление, а не пик ru_maxrss) —
    тогда разница «до/после» построения коллекции осмысленна.
    """
    try:
        with open("/proc/self/status", encoding="utf-8") as status:
            for line in status:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024  # КиБ -> МиБ
    except FileNotFoundError:
        import psutil

        return psutil.Process().memory_info().rss / (1024 * 1024)


def _parse_mem(s: str) -> float:
    s = s.strip()
    units = {
        "GiB": 1024,
        "MiB": 1,
        "KiB": 1 / 1024,
        "B": 1 / 1024 / 1024,
        "GB": 1000,
        "MB": 1,
        "kB": 1 / 1000,
    }
    for u, mul in units.items():
        if s.endswith(u):
            return float(s[: -len(u)]) * mul
    return float(s)


# --- Качество поиска --------------------------------------------------------


def exact_knn(matrix: np.ndarray, query: np.ndarray, k: int) -> np.ndarray:
    """Точный (brute-force) top-k по косинусу = ground truth для recall.

    matrix: (N, d) — все векторы корпуса (предполагаются L2-нормированными).
    query:  (d,)   — вектор запроса (нормирован).
    Возвращает индексы k ближайших.
    """
    sims = matrix @ query
    return np.argpartition(-sims, k)[:k][
        np.argsort(-sims[np.argpartition(-sims, k)[:k]])
    ]


def recall_at_k(approx_ids, exact_ids) -> float:
    """Доля истинных соседей (exact), которые нашёл приближённый поиск."""
    exact_set = set(int(x) for x in exact_ids)
    if not exact_set:
        return 1.0
    hit = sum(1 for x in approx_ids if int(x) in exact_set)
    return hit / len(exact_set)
