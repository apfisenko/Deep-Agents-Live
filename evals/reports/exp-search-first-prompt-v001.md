# Эксперимент: search-first prompt vs baseline

> **Дата:** 2026-06-15 · **Статус:** ✅ завершён
> **Журнал:** [experiments-log.md](experiments-log.md) (E-26)
> **Задача/спринт:** eval-fix loop v0.2 (E-22)

---

## Гипотеза / вопрос

Явное правило «сначала `search_knowledge_base`, потом ответ» + запрет уточняющих вопросов до поиска снизит провалы слоёв `retrieval` (5) и `behavior` (3), поднимет `avg_answer_correctness` с 0.322 без просадки `faithfulness`.

## Конфигурация

| Параметр | Baseline | Candidate |
|---|---|---|
| Ран (имя по E-9) | `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z` | `candidate-search-first-prompt--e2e-qa--5eedd7a1--20260615T194334Z` |
| config_id | `baseline-react-inmemory` | `candidate-search-first-prompt` |
| **Отличие (ровно одно, E-7)** | — | промпт `SYSTEM_PROMPT_SEARCH_FIRST` |
| Промпт | `SYSTEM_PROMPT` | `SYSTEM_PROMPT_SEARCH_FIRST` |
| Датасет (версия) | e2e/e2e-qa **v001** | e2e/e2e-qa **v001** |
| model | `openai/gpt-4o-mini`, temp 0.2 | то же |
| judge | `google/gemini-2.5-flash-lite` | то же |

Ссылки:
- [baseline report](baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z.txt)
- [candidate report](candidate-search-first-prompt--e2e-qa--5eedd7a1--20260615T194334Z.txt)
- [compare](compare-baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z-vs-candidate-search-first-prompt--e2e-qa--5eedd7a1--20260615T194334Z.md)
- [candidate analysis](analysis-candidate-search-first-prompt--e2e-qa--5eedd7a1--20260615T194334Z.md)

> Прогон `...194122Z` аннулирован: backend не видел новый config_id (400 на все items).

## Результаты

| Метрика | Роль | Порог | Baseline | Candidate | Delta |
|---|---|---|---|---|---|
| avg_answer_correctness | **главная** | ≥ 0.75 | 0.322 | **0.090** | **-0.232** |
| avg_faithfulness | guard | ≥ 0.85 | 0.699 | **0.000** | -0.699 |
| avg_answer_relevancy | guard | ≥ 0.80 | 0.455 | **0.079** | -0.376 |
| error_rate | guard | ≤ 0.05 | 0.000 | 0.000 | 0.000 |

**Items с заметным сдвигом:** улучшился 1 (`e2e-qa-ext-013` +0.336); регрессии 11 items (в т.ч. `e2e-qa-syn-001/002` с 0.7+ → 0).

## Наблюдения / находки

1. **Гипотеза не подтвердилась:** главная метрика и оба guard просели.
2. Агент **вызывает** `search_knowledge_base_tool` (tool spans в трейсах), но в experiment output **0 contexts** на всех 24 items → `faithfulness=0` (RAGAS без contexts).
3. Поведение сместилось к отказу: «в базе нет информации» вместо попытки ответить → correctness падает, особенно на syn-items где baseline давал частично верные ответы.
4. Единственный заметный выигрыш: `e2e-qa-ext-013` (+0.336 correctness).
5. Слой провалов candidate: **retrieval 24/24** (все items без contexts в eval-output).

## Решение

**[x] Отклонён** — главная -0.232, faithfulness и relevancy просели. Конфиг остаётся в `configs/` как зафиксированный отрицательный результат.

Обоснование: search-first prompt усилил вызов tool, но не улучшил захват contexts в eval pipeline и заставил агента чаще отказываться от ответа. **Уточнение:** корневая причина — пустой RAG-index после рестарта (manifest skip). Baseline остаётся эталоном.

## Следующие шаги

- [ ] Разобрать, почему contexts=0 при наличии tool spans (SSE capture vs пустой search)
- [ ] Следующая итерация: KB/dataset alignment (`kb_gap`, 11 items) или улучшение search-query/retrieval
- [ ] Рассмотреть гибрид: search-first + обязательная передача contexts в eval output
