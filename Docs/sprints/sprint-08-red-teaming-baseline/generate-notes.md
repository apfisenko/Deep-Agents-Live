# Generate notes — redteam scenarios (задача 06)

> **Дата:** 2026-07-25  
> **Конфиг:** [`practice/redteam/promptfooconfig.yaml`](../../practice/redteam/promptfooconfig.yaml) (без изменений после задачи 05)

---

## Команда

```powershell
$env:Path = "$env:LOCALAPPDATA\nodejs-promptfoo;$env:Path"
cd practice\redteam
npx promptfoo@latest redteam generate -c promptfooconfig.yaml
```

Повторный запуск без `--force`: *No changes detected … Skipping generation* — ожидаемо, файл уже существует.

---

## Метаданные

| Поле | Значение |
|------|----------|
| Выходной файл | `practice/redteam/redteam.yaml` (дефолт Promptfoo; в README — alias `redteam-tests.yaml`) |
| Generated (header) | 2026-07-25T16:32:51.887Z |
| Promptfoo | 0.121.19 (CLI через portable Node v22.22.0) |
| Attack/grader model | `openrouter:openai/gpt-4o-mini`, `showThinking: false` |
| Total cases | **30** |
| Plugins | hijacking, prompt-extraction, tool-discovery, excessive-agency, policy |
| Strategies | jailbreak:meta (15 базовых + 15 meta = 30) |
| Ручные правки кейсов | нет |

---

## DoD задачи 06

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Файл непустой | ✅ 30 tests |
| 2 | Generate успешен | ✅ (первичный прогон; повтор skip) |
| 3 | promptfooconfig не менялся | ✅ |
| 4 | Метаданные | ✅ этот файл |
