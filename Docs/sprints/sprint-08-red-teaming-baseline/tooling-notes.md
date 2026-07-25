# Tooling notes — Promptfoo + стенд

> **Sprint:** [README](./README.md) · задача 02  
> **Дата:** 2026-07-25

---

## Версии

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| System Node (PATH по умолчанию) | v22.14.0 | **Не подходит** для Promptfoo (`^20.20.0 \|\| >=22.22.0`) |
| Node для Promptfoo | **v22.22.0** | Portable: `%LOCALAPPDATA%\nodejs-promptfoo\` |
| npm (portable) | 10.9.4 | вместе с portable Node |
| Promptfoo | **0.121.19** | `npx promptfoo@latest --version` при PATH с portable Node |

### Как вызывать Promptfoo на этой машине

```powershell
$env:Path = "$env:LOCALAPPDATA\nodejs-promptfoo;$env:Path"
npx promptfoo@latest --version
```

Рекомендация: обновить системный Node до ≥22.22.0, чтобы не зависеть от portable-копии.

---

## Skills (promptfoo/promptfoo @ skills.sh)

Установка:

```text
npx skills add promptfoo/promptfoo --skill promptfoo-provider-setup --skill promptfoo-redteam-setup --skill promptfoo-redteam-run -y
```

| Skill | Путь | Зачем |
|-------|------|-------|
| `promptfoo-provider-setup` | `.agents/skills/promptfoo-provider-setup/` | Провайдеры/targets: HTTP на `POST /chat`, OpenRouter, маппинг vars, smoke подключения (задача 04) |
| `promptfoo-redteam-setup` | `.agents/skills/promptfoo-redteam-setup/` | Генерация redteam-конфига: purpose, plugins, strategies, policy (задача 04) |
| `promptfoo-redteam-run` | `.agents/skills/promptfoo-redteam-run/` | `redteam generate` / `redteam eval`, разбор прогонов, реран (задачи 06, 08, 12) |

---

## Конвенция Windows (обязательно)

| Что | Как |
|-----|-----|
| Все цели Makefile | дублировать через **`.\make.ps1 <цель>`** (не сырой `make` в Git Bash как единственный путь) |
| `docker` / `docker compose` | **только через WSL**, вызывая `.\make.ps1 up|down|ps|logs|compose|docker …` — см. [ADR-0004](../../decisions/0004-windows-make-docker-wsl.md), [README](../../../README.md) |
| Прямой `docker` / `docker compose` в PowerShell | ❌ не использовать |
| Backend / checks | `.\make.ps1 dev-backend`, `.\make.ps1 check-health`, `.\make.ps1 check-chat` |

Дальше по спринту (Qdrant/Neo4j/Langfuse при необходимости): `.\make.ps1 up`, статус — `.\make.ps1 ps`.

---

## Стенд

| Сервис | Статус | Примечание |
|--------|--------|------------|
| Agent Core (`backend`) | ✅ | `.\make.ps1 dev-backend` → uvicorn `:8000` |
| `GET /health` | ✅ **200** | проверено: `.\make.ps1 check-health` / HTTP 200 `{"status":"ok",...}` |
| Compose-зависимости | по необходимости | через `.\make.ps1 up` (WSL), не нативный Docker Desktop CLI из PS |
| `mcp_server` | N/A в этом репо | Отдельного `mcp_server` нет; tools в Agent Core. Для baseline достаточно backend `/health` |

---

## Smoke Promptfoo (не redteam агента)

| Поле | Значение |
|------|----------|
| Конфиг | `practice/redteam/smoke/promptfooconfig.yaml` |
| Суть | provider `echo` + assert `contains: hello` |
| Команда | из каталога smoke, с portable Node в PATH: `npx promptfoo@latest eval -c promptfooconfig.yaml --no-cache` (CLI Node — не docker; инфру стенда по-прежнему только через `.\make.ps1`) |
| Результат | **exit 0**, 1/1 passed (2026-07-25) |
| Eval ID | `eval-jEj-2026-07-25T14:09:39` |

Это проверка CLI, не атака на агента.

---

## Самопроверка DoD (задача 02)

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Node в допустимом диапазоне | ✅ v22.22.0 (portable); system 22.14.0 — не использовать для promptfoo |
| 2 | Promptfoo установлен | ✅ 0.121.19 |
| 3 | Три skills + «зачем» | ✅ таблица выше |
| 4 | Backend healthy | ✅ GET /health → 200 |
| 5 | Smoke Promptfoo без ошибки CLI | ✅ exit 0, 1 passed |
