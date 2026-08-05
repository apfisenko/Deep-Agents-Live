# Sprint 15: A2A external checker (S6 · Т12, опционально)

> **Версия roadmap:** v1.0-scaling
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Предшественник:** [Sprint 12](../sprint-12-service-split-a2a/README.md) (design doc)
> **Scope:** согласовать отдельно — **Design + spike (A)** или **полная реализация (B)**

**Окружение:** Python **3.11** · Windows: `make.ps1`

---

## Цель спринта

Спроектировать и (по согласованию) реализовать замену `AsyncSubAgent(url=…)` на **A2A-клиент** для сценария «checker — чужой вендор / другой фреймворк».

---

## Боль / мотивация

Agent Protocol работает, пока обе стороны наши. Checker-SaaS или чужой стек → companion становится **A2A-клиентом**.

---

## Тезис

**Протокол = функция границы (клиентская сторона).** S3 дал A2A-сервер (витрина); S6 — клиент. Цена: таблица «строим сами» в `docs/a2a-integration-design.md`.

---

## DoD — уровень A (Design + spike, минимум)

| # | Критерий |
|---|----------|
| 1 | `docs/a2a-integration-design.md` актуален |
| 2 | ADR `010-a2a-client-adapter.md` |
| 3 | Spike: mock A2A или curl `:2025` → message/send + tasks/get |
| 4 | План замены 5 job-tools без смены промптов companion |

---

## DoD — уровень B (полная реализация, по запросу)

| # | Критерий |
|---|----------|
| 1 | `A2ACheckerAdapter` при `CHECKER_MODE=a2a` |
| 2 | Discovery + cache agent card |
| 3 | Тулы start/check/cancel/list — та же сигнатура для LLM |
| 4 | `async_tasks` из tasks/get |
| 5 | Steering: cancel+resend (базовый); follow-up — флаг |
| 6 | Frontend poller branch для A2A |
| 7 | Tests mock JSON-RPC |

---

## Задачи (уровень B)

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | a2a-client-core | 📋 | [plan](tasks/01-a2a-client-core/plan.md) | — |
| 02 | job-tools-facade | 📋 | [plan](tasks/02-job-tools-facade/plan.md) | — |
| 03 | env-mode-switch | 📋 | [plan](tasks/03-env-mode-switch/plan.md) | — |
| 04 | frontend-a2a-poller | 📋 | [plan](tasks/04-frontend-a2a-poller/plan.md) | — |
| 05 | tests-session-log | 📋 | [plan](tasks/05-tests-session-log/plan.md) | — |

---

## Задача 01: a2a-client-core

- [ ] `src/course_companion/subagents/a2a_checker.py`
- [ ] GET `/.well-known/agent-card.json`
- [ ] JSON-RPC: `message/send`, `tasks/get`, `tasks/cancel`

---

## Задача 02: job-tools-facade

Таблица маппинга (из design doc):

| Было (Agent Protocol) | A2A |
|-----------------------|-----|
| start_async_task | message/send |
| check_async_task | tasks/get + artifacts |
| cancel_async_task | tasks/cancel |
| update_async_task | cancel + resend OR follow-up |
| list_async_tasks | локальный реестр |

---

## Задача 03: env-mode-switch

```bash
CHECKER_MODE=agent_protocol   # default (S2–S4)
CHECKER_MODE=a2a
A2A_CHECKER_URL=http://...
```

---

## Задача 04: frontend-a2a-poller

- [ ] При `CHECKER_MODE=a2a` — poll `tasks/get` вместо LangGraph runs

---

## Задача 05: tests-session-log

- [ ] Mock JSON-RPC server
- [ ] `examples/phase6/a2a-client-log.txt`

---

## За бортом S6

- Auth на A2A (упомянуть в ADR)
- Кастомный agent card
- Push notifications (бонус)

---

## Итог (заполняется после закрытия)

—
