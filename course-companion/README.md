# Course Companion

Диалоговый CLI-ассистент для студентов курса **Deep Agents**.  
Вопросы по курсу, сдача домашнего задания и разбор фидбека — в одном чате.

---

## Быстрый старт

```powershell
cp .env.example .env
# Заполните OPENROUTER_API_KEY в .env

uv sync          # установить зависимости
.\make.ps1 test  # убедиться, что всё работает
uv run companion # запустить CLI
```

**Пример сессии:**

```
Course Companion v0.1 | Ctrl+C для выхода

Вы: Когда дедлайн ДЗ-3?
[router] → qa
[tool]   read_kb_doc: homework.md
Дедлайн третьего домашнего задания — 15 сентября...

Вы: Хочу сдать ДЗ по теме multi-agent, путь ./hw3/
[router] → homework
[mode]   qa → homework
[task]   → homework-checker
[task]   ✓ 5 аспектов, балл 0.74
[mode]   homework → review
Проверка завершена. Рубрика: multi-agent. Балл: 0.74...
```

---

## Паттерны

Course Companion демонстрирует пять мультиагентных паттернов LangChain/LangGraph:

| Паттерн | Реализация | Описание |
|---------|-----------|----------|
| **CompiledSubAgent** | `src/course_companion/subagents/homework_checker.py` | `build_homework_checker()` — граф-адаптер поверх `MentorOrchestrator`; ошибки → AIMessage |
| **DeclarativeSubAgent** | `src/course_companion/subagents/course_qa.py` | `COURSE_QA_SPEC` — dict с промптом и тулами чтения `kb/*.md` |
| **Handoffs** | `src/course_companion/agent/middleware.py` | Один Companion + middleware; переход режима = тул-вызов (`Command`) |
| **Router** | `src/course_companion/router/router.py` | Structured output, `Literal["qa","homework","stay"]`; fail-safe → `stay` |
| **Custom Workflow** | `src/course_companion/graph/graph.py` | `StateGraph`: Router-узел → Companion-узел → END; `InMemorySaver` |

---

## Режимы Companion

```
qa       — вопросы о курсе (расписание, программа, FAQ)
homework — приём и проверка домашнего задания
review   — разбор фидбека и план исправлений
```

Переходы между режимами управляются через тулы-переходы:

```
qa ──switch_to_homework──► homework ──complete_homework──► review
                                                              │
review ──return_to_qa────────────────────────────────────────►qa
review ──resubmit_homework──► homework
```

---

## Структура проекта

```
course-companion/
├── src/course_companion/
│   ├── agent/
│   │   ├── companion.py      # build_companion() — ReAct + middleware
│   │   ├── middleware.py     # select_prompt, filter_tools, build_modes_middleware
│   │   ├── models.py
│   │   └── tools/
│   │       └── mode_tools.py # тулы-переходы + функциональные тулы
│   ├── graph/
│   │   ├── graph.py          # build_graph() — StateGraph
│   │   └── state.py          # CourseCompanionState, HWArtifacts
│   ├── router/
│   │   ├── intent.py         # Intent, RouterInput
│   │   └── router.py         # route() — structured output + fail-safe
│   ├── skills/
│   │   ├── resolver.py       # resolve_rubric(topic) — поиск рубрики по ключевым словам
│   │   └── multi-agent/
│   │       ├── rubric.yaml   # рубрика проверки (5 аспектов × 0.20)
│   │       └── SKILL.md      # system prompt для LLM-рецензента
│   ├── subagents/
│   │   ├── course_qa.py      # DeclarativeSubAgent — kb-тулы
│   │   └── homework_checker.py # CompiledSubAgent — граф-адаптер
│   ├── cli.py                # main() — REPL с stream_mode="updates"
│   └── config.py             # Config из .env
├── tests/
│   ├── e2e/test_four_turns.py  # E2E-тест четырёх ходов (mock LLM)
│   ├── graph/                  # StateGraph тесты
│   ├── router/                 # Router + Intent тесты
│   ├── skills/                 # resolve_rubric тесты
│   ├── subagents/              # homework-checker, course-qa тесты
│   └── agent/                  # middleware, mode_tools тесты
├── docs/decisions/             # ADR 001–005
├── examples/session-log.md     # живой прогон четырёх ходов
├── data/kb/                    # база знаний курса (*.md)
├── .env.example
├── Makefile
├── make.ps1
└── pyproject.toml
```

---

## Ключевые компоненты

### `agent/companion.py` — ReAct-агент
`build_companion(state)` создаёт `create_react_agent` с middleware-оберткой.  
Middleware (`build_modes_middleware`) подменяет системный промпт и набор тулов в зависимости от текущего `state["mode"]`.

### `agent/middleware.py` — конечный автомат режимов
- `MODE_PROMPTS` — промпты для режимов `qa`, `homework`, `review`
- `MODE_TOOL_BLACKLIST` — blacklist тулов по режиму (новый тул доступен везде по умолчанию)
- `select_prompt(mode)` / `filter_tools(mode, tools)` — чистые функции, тестируемые независимо

### `agent/tools/mode_tools.py` — тулы-переходы и операции
| Тул | Действие |
|-----|---------|
| `switch_to_homework` | qa → homework |
| `complete_homework(hw_artifacts)` | homework → review, сохраняет `HWArtifacts` |
| `return_to_qa` | review → qa |
| `resubmit_homework` | review → homework |
| `ask_course_qa(question)` | вызов DeclarativeSubAgent course-qa |
| `run_homework_check(path, topic)` | вызов CompiledSubAgent homework-checker, сохраняет отчёт |
| `explain_feedback(aspect_id)` | объяснение замечания по аспекту из `hw_artifacts` |
| `show_fix_plan()` | план исправлений с баллом |

### `graph/state.py` — состояние диалога
```python
class HWArtifacts(BaseModel):
    topic: str          # тема ДЗ
    rubric_name: str    # имя рубрики
    feedback: list      # замечания из FinalFeedback.issues
    fix_plan: list      # шаги из FixPlan (required + optional)
    score: float | None # 0.0–1.0, формула: 1.0 − req×0.15 − opt×0.05
```

Порог прохождения: `PASS_THRESHOLD = 0.70`.

### `router/router.py` — классификация намерений
Structured output (`Intent`) с тремя вариантами: `qa`, `homework`, `stay`.  
Режим `review` не включён в Router — переход только через тул `complete_homework`.  
Failsafe: любая ошибка LLM → `stay` с `confidence=0.0`.

### `skills/resolver.py` — матчинг рубрик
`resolve_rubric(topic)` перебирает `src/skills/*/rubric.yaml` и ищет совпадение по `match_keywords`.  
Поддерживает fuzzy-поиск (подстрока). При отсутствии совпадения — `FileNotFoundError`.

### `subagents/homework_checker.py` — CompiledSubAgent
`build_homework_checker(path, topic)` собирает граф из одного узла `run_mentor`.  
Вычисляет `score` из `FinalFeedback.issues`, пакует `{score, fix_plan, feedback}` как JSON-метаданные в конец AIMessage.  
`mode_tools._extract_hw_metadata()` распаковывает их при получении результата.

### `subagents/course_qa.py` — DeclarativeSubAgent
`COURSE_QA_SPEC` — dict с системным промптом и двумя тулами: `list_kb_docs`, `read_kb_doc`.  
Читает файлы только из `data/kb/` (path traversal заблокирован).

---

## Make-цели

```powershell
.\make.ps1 dev        # co-deployed: оба графа :2024 + веб-чат :5173
.\make.ps1 checker    # распил: checker :2025
.\make.ps1 companion  # распил: companion :2024 (CHECKER_URL)
.\make.ps1 frontend   # распил: веб-чат :5173 (CHECKER_PROXY_TARGET)
.\make.ps1 compose-up        # поднять / перезапустить (без rebuild)
.\make.ps1 compose-up-build  # пересборка образов
.\make.ps1 compose-down      # погасить контейнеры
.\make.ps1 compose-status    # статус + HTTP-probe
.\make.ps1 stop       # освободить порты 2024/2025/5173
.\make.ps1 cli        # CLI REPL (без сервера)
.\make.ps1 test       # все тесты
.\make.ps1 lint       # ruff + tsc фронта
.\make.ps1 typecheck  # mypy
.\make.ps1 ci         # lint + typecheck + test
```

---

## Ступень 1: Agent Server + веб-чат

Тот же граф доступен через HTTP — браузерный чат со стримингом и `thread_id`, переживающим F5.

```powershell
cd frontend && npm install   # первый раз (.npmrc: legacy-peer-deps)
.\make.ps1 dev
# Agent Server: http://localhost:2024/info
# Веб-чат:     http://localhost:5173
.\make.ps1 stop
```

**`--no-reload` обязателен:** проверка ДЗ пишет в `.mentor-workspace/`; hot reload dev-сервера перезапускает процесс посреди рана.

CLI без изменений: `uv run companion`. Сдача ДЗ в S1 синхронная — поле ввода «занято» 1–3 мин.

---

## Ступень 2: async-checker (Sprint 11)

Фоновая проверка: сдача → ack мгновенно; карточка «проверяется…»; QA параллельно; фидбек приходит сам (поллер во фронте).

```powershell
.\make.ps1 dev
# curl localhost:2024/info  → graphs: companion, checker
```

### §4.1 Pitfall: `--n-jobs-per-worker`

Dev-сервер LangGraph по умолчанию даёт **1 worker-slot**. Активный ран чекера съедает его — «асинхронная» проверка снова блокирует чат.

**Mitigation:** `make dev` / `make.ps1 dev` передают `--n-jobs-per-worker 10` (`JOBS=10` в Makefile).

| Конфиг | Слотов | Поведение |
|--------|--------|-----------|
| дефолт (1) | 1 | check блокирует companion |
| `JOBS=10` | 10 | фоновый check + параллельный чат |

CLI (`uv run companion`) — sync checker, ждёт 1–5 мин (без изменений).

---

## Ступень 3: распил + A2A (Sprint 12)

Checker — отдельный процесс `:2025`; companion ходит по HTTP (`CHECKER_URL`). Код companion не меняется — только конфиг + env.

```powershell
.\make.ps1 checker    # :2025 — langgraph.checker.json
.\make.ps1 companion  # :2024 — langgraph.companion.json + CHECKER_URL
.\make.ps1 frontend   # :5173 — CHECKER_PROXY_TARGET для поллера
# браузер: http://localhost:5173
.\make.ps1 stop
```

| Env | Где | Назначение |
|-----|-----|------------|
| `CHECKER_URL=http://localhost:2025` | companion | AsyncSubAgent HTTP |
| `CHECKER_PROXY_TARGET=http://127.0.0.1:2025` | frontend | poller proxy |

**A2A-витрина** checker'а — нативная возможность Agent Server (0 строк нашего кода):

```powershell
curl -X POST http://localhost:2025/assistants/search -d '{}'
curl "http://localhost:2025/.well-known/agent-card.json?assistant_id=<uuid>"
```

Полный walkthrough: [`examples/walkthrough/a2a-showcase.txt`](examples/walkthrough/a2a-showcase.txt).

**Мягкий отказ:** остановите checker — `start_async_task` вернёт текстовую ошибку, `async_tasks` останется пустым, QA работает. Лог: [`examples/phase3/down-remote.txt`](examples/phase3/down-remote.txt).

Co-deployed (`.\make.ps1 dev`) — регрессия ступеней 1–2, оба графа на `:2024`.

---

## Docker compose (Sprint 14)

Распил из ступени 3, упакованный в три контейнера одной командой. **Docker только через WSL** на Windows.

```powershell
cp .env.example .env   # OPENROUTER_API_KEY обязателен
.\make.ps1 compose-up
# веб-чат: http://localhost:5173
.\make.ps1 compose-status   # все OK + HTTP 200
.\make.ps1 compose-down
```

Если `compose-status` показывает **Exited (143)** — контейнеры получили SIGTERM. Частые причины на Windows:
- `make stop` / `make.ps1 stop` при compose (убивает docker-proxy) — **используйте только `compose-down`**
- Docker Desktop → Settings → **Resource Saver** — отключите или добавьте исключение

| Сервис | Порт | Образ / команда |
|--------|------|-----------------|
| checker | 2025 | Python-образ, `langgraph.checker.json` |
| companion | 2024 | тот же образ, `langgraph.companion.json`, `CHECKER_URL=http://checker:2025` |
| frontend | 5173 | `node:22-slim`, Vite dev |

Как устроено (`docker-compose.yml`, `Dockerfile`, `frontend/Dockerfile`):

- **Один Python-образ — два сервиса.** Companion и checker из одного Dockerfile; сервис = команда запуска (`--config`, порт).
- **Адреса на швах — hostnames compose-сети:** `CHECKER_URL=http://checker:2025`, прокси фронта — `http://companion:2024` и `http://checker:2025`. Обязателен `--host 0.0.0.0`: по умолчанию `langgraph dev` и Vite слушают localhost и снаружи контейнера невидимы.
- **`.env` не в образе** — монтируется `:ro` при старте.
- **Общий том `mentor-workspace`** — артефакты проверок в `ai-homework-mentor/workspace/`; checker пишет, companion читает в review.

**A2A-витрина checker'а с хоста:**

```powershell
curl -X POST http://localhost:2025/assistants/search -d '{}'
curl "http://localhost:2025/.well-known/agent-card.json?assistant_id=<uuid>"
```

**Честная пометка:** внутри контейнеров — `langgraph dev` (dev-сервер): state в памяти, `docker compose down` = все треды пропали. **Не смешивайте с портовым запуском:** `make stop` / `make.ps1 stop` убивают процесс на портах — при compose это docker-proxy, контейнеры получат SIGTERM. Гасить compose только через `compose-down`.

Портовый запуск (ступени 1–3) — равноправный запасной путь без Docker.

---

## Архитектурные решения

Обоснование ключевых решений зафиксировано в ADR:

- [ADR 001](docs/decisions/001-vendored-mentor.md) — editable path для `ai-homework-mentor`
- [ADR 002](docs/decisions/002-compiled-vs-declarative-subagent.md) — CompiledSubAgent vs DeclarativeSubAgent
- [ADR 003](docs/decisions/003-single-agent-middleware-handoffs.md) — один Companion + middleware
- [ADR 004](docs/decisions/004-router-literal-no-review.md) — `review` не входит в Router Literal
- [ADR 005](docs/decisions/005-inmemory-checkpointer.md) — InMemorySaver для v1 CLI
- [ADR 006](docs/decisions/006-agent-server-export.md) — Agent Server export, два режима checkpointer
- [ADR 007](docs/decisions/007-async-checker-agent-protocol.md) — async checker, Agent Protocol, co-deployed
- [ADR 008](docs/decisions/008-protocol-by-boundary.md) — Agent Protocol vs A2A по границе
- [A2A integration design](docs/a2a-integration-design.md) — companion как A2A-клиент (design only)

---

## Документация

- [Roadmap](roadmap.md) — план версий и статус спринтов
- [Архитектура](concept/architecture.md)
- [Видение](concept/vision.md)
