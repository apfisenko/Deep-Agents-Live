# Plan — Task 03: make-targets

**Sprint:** sprint-01-scaffold  
**Статус:** 🚧 In Progress  
**Дата:** 2026-08-02

---

## Цель

Создать единую точку входа: `Makefile` (WSL/Linux) и `make.ps1` (Windows PowerShell).

---

## Состав работ

- [ ] `Makefile` — цели: `dev`, `test`, `lint`, `format`, `typecheck`, `ci`
- [ ] `make.ps1` — PowerShell-эквивалент с параметром `[string]$Target`

---

## DoD

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `.\make.ps1 test` PASSED | PowerShell |
| 2 | `.\make.ps1 lint` зелёный | PowerShell |
| 3 | `.\make.ps1 ci` без ошибок | PowerShell |
