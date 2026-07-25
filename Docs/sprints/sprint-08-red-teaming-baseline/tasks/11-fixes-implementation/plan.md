# Plan: Task 11 — Реализация фиксов

> **Sprint:** [README](../../README.md) · задача 11  
> **Дата:** 2026-07-25  
> **Вход:** [`fix-decisions.md`](../../fix-decisions.md)

---

## Цель

Реализовать FIX-01…FIX-04 за `SECURITY_ENABLED` (default on), тесты, `.env.example`. Redteam yaml не трогать.

---

## Состав работ

1. `Settings.security_enabled` + `.env.example`
2. `backend/app/security/` — payment_state, input_guard, output_sanitizer, prompt appendix
3. `tools/registry.py` — session-scoped payment guard
4. `react_agent.py` — pre/post guards, tool result tracking
5. `tests/test_security.py` + conftest
6. ruff + pytest

---

## DoD

| # | Критерий |
|---|----------|
| 1 | SECURITY_ENABLED default on |
| 2 | FIX-01…04 в коде |
| 3 | false = bypass |
| 4 | SECURITY_BLOCKED stable |
| 5 | lint/tests pass |
| 6 | redteam yaml unchanged |
