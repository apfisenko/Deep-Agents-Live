# Eval-fix loop — OSS model: gpt-oss-120b:free

> **Дата:** 2026-06-17 · **E-22 / E-8 benchmark-only**

## Гипотеза

Бесплатная OSS-модель `openai/gpt-oss-120b:free` (OpenRouter) даст прирост **generation**-слоя vs `gpt-4o-mini` за счёт более сильного reasoning при сохранении tool calling.

## Изменение (E-7)

**Только model.name** — `openai/gpt-4o-mini` → `openai/gpt-oss-120b:free`. Prompt/KB/judge без изменений.

> Backend: `127.0.0.1:8001` (candidate configs не резолвятся на stale :8000).

## Baseline

| run | avg_answer_correctness | avg_faithfulness |
|---|---|---|
| `baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T172234Z` | 0.339 | 0.729 |

## Результаты

| Метрика | Baseline | OSS 120b | Delta |
|---|---|---|---|
| avg_answer_correctness | 0.339 | **0.312** | **−0.027** |
| avg_faithfulness | 0.729 | 0.716 | −0.013 |
| avg_answer_relevancy | 0.418 | 0.421 | +0.003 |
| error_rate | 0.000 | 0.000 | 0 |

**Слои:** generation **17**, behavior 5, retrieval 2 (kb_gap 0 — модель отвечает без KB, но не точнее).

Smoke: 0 tool-events в SSE при одном запросе — типичный OSS-паттерн (E-8 metrics-guide).

## Решение (E-26)

**reject deploy** — главная метрика ниже baseline (−0.027). Guard faithfulness не пройден. OSS free не заменяет gpt-4o-mini для ReAct+tools.

## Ссылки

- Run: `candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T175047Z`
- [compare vs baseline](compare-baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T172234Z-vs-candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T175047Z.md)
- [analysis](analysis-candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T175047Z.md)
