# Контраст S3 vs S4

> Заполнено после реализации S4 (2026-07-24).
> Источник S3: [pain-s3.md](./pain-s3.md)

---

## Тезис

S3 показал, что CE не заменяет декомпозицию: контекст родителя всё равно раздувается.
S4 переносит тяжёлую проверку в изолированные reviewer-окна; родитель видит только brief → summary + путь к note.

---

## Метрики (fixture `tests/fixtures/large_hw`)

| Метрика | S3 (single agent) | S4 (subagents) |
|---------|-------------------|----------------|
| Max parent context tokens (estimate) | ~980 (после summarize) | ~2230 (live `20260724T173923Z`) |
| Summarize events (parent) | 1 | 0 (production thresholds) |
| Offload events (parent) | 1 | 0 |
| Review notes per aspect | 1 общий поток | 2: `review_architecture.md`, `review_code_quality.md` |
| Subagent handoffs (verbose) | 0 | 2 |
| Ощущение «мутности» | высокое | ниже — аспекты изолированы, notes в файлах |

Числа S3 — CI с заниженными порогами CE, см. [pain-s3.md](./pain-s3.md).
Числа S4 — live OpenRouter (`logs/summary_log_20260724T173923Z.md`). Parent tokens могут расти из‑за summaries в thread; **полные notes** остаются в `/notes/`, не в контексте родителя.

---

## Что видно в verbose

| S3 | S4 |
|----|-----|
| context engineering: рост до ~980, summarize + offload | subagents panel: brief/summary/note per aspect |
| один агент читает много файлов | subagents panel: 2 handoff + note paths |
| notes — общий поток | `delegated: architecture, code_quality` в compact |

---

## Команда сравнения

```powershell
cd ai-homework-mentor
# S4 (subagents) — тот же источник, что в pain-s3:
.\make.ps1 run -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli" -Verbose
```

Ожидание: секция **subagents** с двумя handoff; review-ноты в `/notes/`; summary log в `logs/summary_log_<session>.md`.

---

## Вывод

Изоляция окон закрывает боль S3 («одному агенту тесно») лучше, чем только CE. CE остаётся страховкой у родителя и детей, но не заменяет reviewer-субагентов.
