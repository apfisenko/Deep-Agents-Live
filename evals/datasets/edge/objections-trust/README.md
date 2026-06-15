# Датасет: objections-trust

**Группа:** edge · **Версия:** v001 (`v001_2026-06-15.yaml`) — **reviewed** · synced Langfuse

## Что проверяет

**G4/G5:** демо, цена, скепсис, format-mismatch — без ложных обещаний; эталон = факты из KB.

## v001 stats (target)

| | |
|---|---|
| Items | 11 |
| Real / synthetic | 5 / 6 |
| Intents | objection, format-mismatch |
| `approximate` | ext-011, ext-012, obj-syn-004 (расписание live) |

## Политики (KB)

- **Возврат 14 дней** — verified во всех programs/*.md
- **Нет публичных демо всех курсов** — `ai-agents-combo.md`

## Метрики (task 07)

`answer_correctness`, `faithfulness`, `fact_coverage` — [metrics-map.md](../../../../Docs/eval/metrics-map.md)

## Langfuse

`edge/objections-trust/v001` — после review.
