# Sprint 01: Парсинг входа + получение кода

> **Версия roadmap:** v0.2 (спринты S0–S9)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-07-24
> **Закрыт:** 2026-07-24
> **Зависит от:** [Sprint 00](../sprint-00-skeleton/README.md) ✅ (каркас CLI + агент + YAML + логи)

---

## Цель спринта

Из пользовательского входа извлекаются источник кода и тема задания; код доступен локально (чтение директории или shallow-клон публичного GitHub); при нехватке данных — один уточняющий вопрос, без домыслов.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | После S0 агент отвечает «в воздух»: не знает *что* проверять и *откуда* брать код |
| **Боль, которую оставляем явно** | Код получен, но нет rubric, todo-плана, workspace-структуры артефактов и feedback по критериям (это S2) |
| **Механизм deep-agent** | Вход агента как контекст; политика «уточнять, а не выдумывать» |
| **Сквозные атрибуты** | Rich CLI (compact/verbose), OpenRouter, YAML-промпты, логирование — уже из S0 |

### Граница с S2 (важно)

В S1 появляется **минимальный staging** для кода (`workspace/code/` или согласованный эквивалент): туда копируется/клонируется исходник. Полная раскладка workspace (`input/`, `rubric/`, `notes/`, `output/`), todo и rubric-файл — **только в S2**. Не раздувать S1 до E2E-проверки.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Из входа извлекаются `source` (path \| github_url) и `topic` | ✅ unit-тесты + verbose CLI |
| 2 | Локальная директория: файлы кода доступны агенту/staging (без исполнения) | ✅ fixture + live run |
| 3 | Публичный GitHub: shallow clone в staging | ✅ unit с моком git |
| 4 | Неполный вход → ровно один уточняющий вопрос, тема/URL не выдуманы | ✅ exit 2, без fetch |
| 5 | CLI принимает и свободный текст, и `-Path` | ✅ |
| 6 | Код студента / клон **не исполняется** (нет `subprocess` запуска студенческого entrypoint) | ✅ review + тесты политики |
| 7 | Verbose + tests зелёные | ✅ |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S1 |
|-------|------------|
| `deep-agents-core` | Расширение агента: tool/шаг парсинга и fetch без субагентов |
| `schema-guided-reasoning` | Структурированный разбор входа (source + topic + needs_clarification) |
| `modern-python` | Файловый I/O, pathlib, тесты |
| `python-testing-patterns` | Фикстуры: локальный mini-repo, мок `git clone` |
| `sharp-edges` | Таймауты внешних вызовов (`git`), fail-fast на битый путь/URL |

Роутеры: [`.cursor/rules/methodology/40-skills-router.mdc`](../../../.cursor/rules/methodology/40-skills-router.mdc).

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Модель Submission + парсинг входа | ✅ | [plan](tasks/01-parse-submission/plan.md) | [summary](tasks/01-parse-submission/summary.md) |
| 02 | Получение кода: локальная директория | ✅ | [plan](tasks/02-local-code/plan.md) | [summary](tasks/02-local-code/summary.md) |
| 03 | Получение кода: GitHub shallow clone | ✅ | [plan](tasks/03-github-clone/plan.md) | [summary](tasks/03-github-clone/summary.md) |
| 04 | Склейка в CLI + политика уточнения | ✅ | [plan](tasks/04-cli-clarify/plan.md) | [summary](tasks/04-cli-clarify/summary.md) |

---

## Задача 01: Модель Submission + парсинг входа ✅

### Цель

Вход пользователя превращается в структурированный `Submission` (источник + тема + флаг «нужно уточнение»).

> 💡 **Скиллы:** `schema-guided-reasoning`, `deep-agents-core`.

### Состав работ

- [ ] Pydantic-модель: `source_type` (`local_path` \| `github_url` \| `unknown`), `source_value`, `topic` (optional), `raw_text`, `needs_clarification`, `clarification_question`
- [ ] Парсер: эвристики URL/пути + LLM-разбор темы из свободного текста (промпт в YAML)
- [ ] Политика: если нет источника **или** нет темы → `needs_clarification=True`, один конкретный вопрос; не подставлять «типовую» тему
- [ ] Промпт парсера в `config/prompts/parse_submission.yaml`
- [ ] Unit-тесты на фикстурах текста (с URL, с путём, без темы, мусор)
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | URL GitHub распознаётся | pytest на фикстурах |
| 2 | Без темы → clarification, topic пустой | pytest |
| 3 | Промпт парсера в YAML | файл существует; загрузчик читает |

**Пользователь проверяет:**

- На неоднозначном входе вопрос понятен человеку (после задачи 04)

### Артефакты

- `src/.../submission/` — модель + парсер
- `config/prompts/parse_submission.yaml`
- тесты фикстур входа

### Документы

- 📋 [План задачи](tasks/01-parse-submission/plan.md)
- 📝 [Summary](tasks/01-parse-submission/summary.md)

---

## Задача 02: Получение кода — локальная директория ✅

### Цель

По валидному локальному пути код попадает в staging (копия или индексированный снимок), без исполнения.

> 💡 **Скиллы:** `modern-python`, `python-testing-patterns`.

### Состав работ

- [ ] Валидация пути: существует, это директория, доступна на чтение
- [ ] Копирование/снимок в `workspace/code/` (исключения: `.git`, `node_modules`, `__pycache__`, `.venv` — список в конфиге)
- [ ] Манифест: список относительных путей файлов (для CLI verbose и будущего агента)
- [ ] Запрет: не запускать файлы из директории студента
- [ ] Тесты на fixture-директории
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Валидный путь → файлы в staging | pytest |
| 2 | Несуществующий путь → понятная ошибка | pytest |
| 3 | Исключённые каталоги не копируются | pytest |

**Пользователь проверяет:**

- `.\make.ps1 run -- -Path .\concept` (или fixture) показывает в verbose, что код «получен»

### Артефакты

- `src/.../code_fetch/local.py` (или эквивалент)
- `config/agent.yaml` — секция ignore-patterns
- fixture mini-project в `tests/fixtures/local_hw/`

### Документы

- 📋 [План задачи](tasks/02-local-code/plan.md)
- 📝 [Summary](tasks/02-local-code/summary.md)

---

## Задача 03: Получение кода — GitHub shallow clone ✅

### Цель

Публичный репозиторий клонируется shallow в staging; приватные/битые URL — явная ошибка; код не исполняется.

> 💡 **Скиллы:** `sharp-edges` (timeout), `python-testing-patterns` (мок subprocess).

### Состав работ

- [ ] Нормализация GitHub URL (https, `.git`, optional branch/ref — **минимум**: default branch; branch — только если просто)
- [ ] `git clone --depth 1` в `workspace/code/` (или подкаталог сессии)
- [ ] Timeout + обработка: нет `git`, сеть, 404, непубличный репо
- [ ] Тот же манифест файлов, что после локального fetch
- [ ] Тесты с моком `git`; один opt-in интеграционный тест на известный публичный tiny-repo (за флагом/ключом сети)
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Успешный clone (мок) заполняет staging | pytest |
| 2 | Ошибка git → сообщение без traceback пользователю | pytest |
| 3 | Нет исполнения post-clone скриптов | review + отсутствие вызовов |

**Пользователь проверяет:**

- Ручной прогон на маленьком публичном репо (по возможности)

### Артефакты

- `src/.../code_fetch/github.py`
- тесты с моком clone

### Документы

- 📋 [План задачи](tasks/03-github-clone/plan.md)
- 📝 [Summary](tasks/03-github-clone/summary.md)

---

## Развилка (зафиксировать в plan задачи 03 при старте)

Нужно решение перед реализацией задачи 03, если неочевидно:

1. **Только default branch** vs поддержка `url@branch` / `tree/<branch>` в URL  
2. Клон **в процессе** через `git` CLI vs библиотека — рекомендация плана: **git CLI** (проще, прозрачнее в verbose)

По умолчанию в этом README: **default branch + git CLI**. Если нужно иначе — сказать до старта задачи 03.

---

## Задача 04: Склейка в CLI + политика уточнения ✅

### Цель

Единый поток: ввод → parse → (clarify \| fetch) → краткий отчёт в Rich CLI; агент видит структурированный контекст submission + манифест кода.

> 💡 **Скиллы:** `deep-agents-core`.

### Состав работ

- [ ] Оркестрация шага после S0-ответа: сначала parse+fetch, затем ответ агента **с контекстом** «что получено» (ещё не full review)
- [ ] Если `needs_clarification` — CLI печатает вопрос и **завершает без fetch** (exit code согласованный, напр. 2)
- [ ] Compact: источник, тема, число файлов / «нужно уточнение»
- [ ] Verbose: raw parse result, ignore-patterns, путь staging, первые N путей манифеста
- [ ] Логи: parse result ids (не полные дампы ПД), успех/ошибка fetch
- [ ] Обновить `docs/gaps-s0.md` → `docs/gaps-s1.md` (или дополнить): всё ещё нет rubric/плана/feedback
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Полный локальный сценарий зелёный | `.\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: …"` |
| 2 | Неполный вход → вопрос, staging пуст/не тронут | pytest + run |
| 3 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

**Пользователь проверяет:**

- В verbose видно: распознанный source/topic → fetch → манифест
- Нет ложного «feedback по rubric»

### Артефакты

- обновлённый CLI и orchestrator flow
- `docs/gaps-s1.md`

### Документы

- 📋 [План задачи](tasks/04-cli-clarify/plan.md)
- 📝 [Summary](tasks/04-cli-clarify/summary.md)

---

## Демонстрация через Rich CLI

```powershell
cd ai-homework-mentor

# Локальный путь + тема
.\make.ps1 run -- -Path .\tests\fixtures\local_hw -Message "Тема: FastAPI homework" -Verbose

# Текст со ссылкой на GitHub
.\make.ps1 run -- -Message "Проверь https://github.com/org/tiny-repo тема: CLI utility" -Verbose

# Неполный вход — ожидаем уточняющий вопрос
.\make.ps1 run -- -Message "проверь моё дз пожалуйста" -Verbose
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Распознанные source + topic → «код получен: N файлов» **или** один уточняющий вопрос |
| **verbose** | JSON/таблица parse result; путь staging; фрагмент манифеста; лог clone/copy; **нет** todo, rubric-score, субагентов |

---

## Вне scope (не делать в S1)

- Rubric-файл, todo-план, structured homework feedback (S2+)
- Субагенты, skills routing, CE-метрики
- Приватные репозитории, auth GitHub
- Исполнение/тесты кода студента
- Полноценный multi-turn диалог уточнения (достаточно одного вопроса и стопа; продолжение — ручной повтор запуска с дописанным входом)

---

## Итог (заполняется после закрытия)

Sprint 01 закрыт: parse `Submission` → local/GitHub staging в `workspace/code/` → манифест; неполный вход даёт один уточняющий вопрос без fetch. Проверки по rubric / todo / feedback ещё нет — см. [`docs/gaps-s1.md`](../../docs/gaps-s1.md).

---

## Следующий спринт

После «ок» по S1 → разворот **S2** (`sprint-02-workspace-rubric-plan`): workspace + rubric + todo, минимальный E2E одним агентом.
