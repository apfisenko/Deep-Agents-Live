# Ревью конфигурации redteam (задача 05)

> **Дата:** 2026-07-25  
> **Ревьюер:** apfisenko (human)  
> **Конфиг:** [`practice/redteam/promptfooconfig.yaml`](../../practice/redteam/promptfooconfig.yaml)  
> **Explainer:** [`practice/redteam/config-explainer.md`](../../practice/redteam/config-explainer.md)  
> **Target:** [`practice/redteam/target.mjs`](../../practice/redteam/target.mjs)  
> **Вход:** [`plugin-selection.md`](plugin-selection.md), [`threat-model.md`](threat-model.md)

---

## CLI-проверки

| Команда | Результат | Примечание |
|---------|-----------|------------|
| `npx promptfoo validate config -c promptfooconfig.yaml` | ✅ pass | Node **v22.22.0** (portable); system 22.14.0 — не использовать |
| `npx promptfoo validate target -c promptfooconfig.yaml` | ✅ pass | connectivity passed; backend + `qdrant-up` + `dev-backend` |

```powershell
$env:Path = "$env:LOCALAPPDATA\nodejs-promptfoo;$env:Path"
cd practice\redteam
npx promptfoo@latest validate config -c promptfooconfig.yaml
npx promptfoo@latest validate target -c promptfooconfig.yaml
```

---

## Чек-лист по yaml

| # | Пункт | Статус | Доказательство |
|---|-------|:------:|----------------|
| 1 | URL/method: `POST /api/v1/chat` на стенд задачи 02 | ✅ | `target.mjs`: POST → `http://127.0.0.1:8000/api/v1/chat` (или `AGENT_CHAT_URL`); `validate target` OK |
| 2 | Reasoning отключён | ✅ | `redteam.provider.config.showThinking: false`, `temperature: 0` |
| 3 | Имена tools только из фактов спринта | ✅ | purpose: 5 tools — `search_knowledge_base`, `list_b2c_products`, `save_lead`, `create_payment_link`, `confirm_payment` |
| 4 | Policy `confirm_payment` присутствует | ✅ | plugin `policy` + inline text в yaml (совпадает с plugin-selection) |
| 5 | entities = задача 03 | ✅ | 6 B2C: ai-agents-combo, vibe-coding-intensive, fullstack-aidd, agents, deep-agents, consultation |
| 6 | strategies в корректной форме | ✅ | `- jailbreak:meta` (список, не кастомный id) |
| 7 | plugins/strategies/параметры = задача 03 | ✅ | см. таблицу diff ниже |
| 8 | Изоляция session_id | ✅ | `randomUUID()` на каждый вызов в `target.mjs`; общий session не передаётся |
| 9 | defaultTest assert на маркер блокировки | ✅ | javascript assert → `SECURITY_BLOCKED`, always pass, score 0/1 |

---

## Сверка explainer ↔ yaml

| Секция explainer | Совпадает с yaml | |
|------------------|:----------------:|---|
| Target / session isolation | ✅ | |
| defaultTest / SECURITY_BLOCKED | ✅ | |
| purpose PROTECTED/DISCLOSABLE | ✅ | |
| OpenRouter provider | ✅ | |
| Plugins / strategies / params | ✅ | |
| Команды validate | ✅ | validate target прошёл после правки URL в target |

---

## Diff с `plugin-selection.md` (задача 03)

| Поле | plugin-selection | promptfooconfig.yaml | Diff |
|------|------------------|----------------------|------|
| plugins | 5 (hijacking, prompt-extraction, tool-discovery, excessive-agency, policy) | те же 5 | пусто |
| policy text | confirm_payment rule + DISCLOSABLE ok | идентичный смысл | пусто |
| strategies | `jailbreak:meta` only | `jailbreak:meta` | пусто |
| numTests | 3 | 3 (global + per plugin) | пусто |
| entities | 6 B2C | 6 B2C | пусто |
| maxConcurrency | 1 | 1 | пусто |
| provider | OpenRouter, reasoning off | `openrouter:openai/gpt-4o-mini`, `showThinking: false` | пусто |

**Human override (задача 04→05):** убран `url: "{{env.AGENT_CHAT_URL}}"` из yaml — file provider не резолвит `{{env.*}}`; URL задаётся в `target.mjs` (env или default). Задокументировано в explainer.

---

## Замечания / не блокеры

| # | Замечание | Решение |
|---|-----------|---------|
| 1 | Portable Node 22.22.0 обязателен для CLI | `$env:Path = "$env:LOCALAPPDATA\nodejs-promptfoo;$env:Path"` или обновить system Node |
| 2 | Минимальный Docker для redteam | `.\make.ps1 qdrant-up` (не полный `up`) |
| 3 | `session: skipped` в validate target | Ожидаемо: stateless target, изоляция через новый UUID |

---

## Verdict

| | |
|---|---|
| **Статус** | **PASS** |
| **Готовность к `redteam generate`** | Да (задача 06) |
| **Условие** | Не менять yaml между generate и baseline «до/после» без возврата к ревью |

Подпись ревьюера: _apfisenko_, 2026-07-25 — **все 9 пунктов чек-листа проверены вручную, задача 05 закрыта**

---

## Следующий шаг

Задача 06: `npx promptfoo redteam generate` по этому конфигу → `practice/redteam/redteam-tests.yaml`.
