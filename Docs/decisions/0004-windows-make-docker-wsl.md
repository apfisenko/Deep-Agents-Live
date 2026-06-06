# ADR-0004 — Make + PowerShell на Windows, Docker через WSL

> **Статус:** ✅ Accepted
> **Дата принятия:** 2026-06-06
> **Область:** Deep-Agents-Live

---

## Контекст

Основная среда разработки — **Windows**. `make` нативно недоступен; Docker Compose надёжнее через WSL2. Нужен единый интерфейс команд для всех участников.

## Решение

- **`Makefile`** — канонический набор целей (`dev`, `lint`, `test`, `up`, …)
- **`make.ps1`** в корне — зеркало тех же целей для PowerShell на Windows
- **Docker Compose** (Langfuse, backend, frontend, bot) — запуск через **WSL2**
- Разработка Python/Node-кода — нативно на Windows, без обязательного WSL для редактирования кода

## Последствия

- Документация и CI ссылаются на `make`; Windows-разработчики используют `make.ps1`
- В онбординге явно указан путь: WSL для контейнеров, PowerShell для make-целей
