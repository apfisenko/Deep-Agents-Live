# Summary — Task 03: make-targets

**Статус:** ✅ Done  
**Дата:** 2026-08-02

---

## Что сделано

- `Makefile` — цели: `dev`, `test`, `lint`, `format`, `typecheck`, `ci`
- `make.ps1` — PowerShell-эквивалент с `[string]$Target`; `ci` вызывает lint → typecheck → test с цветными заголовками

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `.\make.ps1 test` PASSED | ✅ 2 passed |
| 2 | `.\make.ps1 lint` зелёный | ✅ All checks passed |
| 3 | `.\make.ps1 ci` без ошибок | ✅ lint + typecheck + test |
