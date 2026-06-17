# Eval-fix loop — итерация 3: stronger model gpt-4o

> **Дата:** 2026-06-17 · **Sprint:** eval-03 · **E-22 iter 3**

## Гипотеза

После KB-alignment (baseline 0.339) главный слой провалов — **generation**. Переход `gpt-4o-mini` → `gpt-4o` поднимет avg_answer_correctness на ≥ +0.03 при faithfulness ≥ 0.65.

## Изменение (E-7)

**Только model.name** — `openai/gpt-4o-mini` → `openai/gpt-4o`. Backend: `127.0.0.1:8001`.

## Прогон 173842Z — annulled

Stale :8000 → `config_not_found`, error_rate 1.0. Не учитывается.

## Результаты (валидный прогон `180704Z`)

| Метрика | Baseline | gpt-4o | Delta |
|---|---|---|---|
| avg_answer_correctness | 0.339 | **0.399** | **+0.060** |
| avg_faithfulness | 0.729 | 0.604 | −0.125 |
| avg_answer_relevancy | 0.418 | 0.497 | +0.079 |
| error_rate | 0.000 | 0.000 | 0 |

**Слои:** generation 12, behavior 8, retrieval 4 (kb_gap 0).

**Distribution:** bucket 0.75–1.00: 1 item (vs 0 на baseline); 0.50–0.75: 6 (vs 4).

## Решение (E-26)

**iterate** — гипотеза по главной подтверждена (+0.060 > +0.03), guard faithfulness 🔴 (−0.125). Trade-off: gpt-4o точнее по reference, но чаще дополняет контекст. Следующий шаг: gpt-4o + anti-hallucination prompt или search-fallback (комбо iter 2 + model).

## Ссылки

- Run: `candidate-gpt4o-v001--e2e-e2e-qa----20260617T180704Z`
- [compare vs baseline](compare-baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T172234Z-vs-candidate-gpt4o-v001--e2e-e2e-qa----20260617T180704Z.md)
- [analysis](analysis-candidate-gpt4o-v001--e2e-e2e-qa----20260617T180704Z.md)
