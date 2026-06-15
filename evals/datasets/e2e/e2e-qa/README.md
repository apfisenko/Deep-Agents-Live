# Датасет: e2e-qa

**Группа (слой):** e2e  
**Текущая версия:** v001 (`v001_2026-06-15.yaml`)  
**Формат:** YAML (E-12)

## Что проверяет

End-to-end ответ B2C-клиента на реальный вопрос: retrieval + формулировка (главный vertical slice, E-18).

## Источник items

| Источник | Кол-во | Примечание |
|----------|--------|------------|
| `dataset/v0.1.jsonl` real (ext-*) | 12 | B2B исключены → segment-routing |
| `dataset/v0.1.jsonl` synthetic (syn-*) | 9 | из `data/b2c/programs/` |
| **Итого v001** | **24** | ≥20 DoD |

## Метрики

Из [metrics-map.md](../../../../Docs/eval/metrics-map.md): `answer_correctness` (главная item), `faithfulness`, `answer_relevancy`, `task_error`.

## Честность ground truth (E-14)

| gt_quality | Items | Причина |
|------------|-------|---------|
| `verified` | 21 | synthetic + real с фактами из KB |
| `approximate` | 3 | ext-009, ext-011, ext-012 — даты/«14 дней» вне явного KB |

## Правила пополнения

- Правка = новый файл `v002_YYYY-MM-DD.yaml` (E-11)
- Эталон утверждает человек до `reviewed_by` (E-13)
- Стиль эталона: сжатый Markdown для виджета (dataset-map)

## Зеркало в Langfuse (E-16)

**folders-as-versions:** датасет `e2e/e2e-qa/v001`
