# Task 05: Backend smoke-тесты

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-3-smoke-tests`
> **Spec:** [api-contracts.md](../../../../concept/api-contracts.md); conventions — тестирование

---

## Цель

Минимальный pytest-набор для Agent Core: smoke health endpoint и проверка fail-fast конфигурации.

---

## Состав работ

- [ ] Добавить dev-зависимости: pytest, pytest-asyncio, httpx (если не добавлены)
- [ ] Создать `backend/tests/conftest.py` — фикстура `TestClient` / `AsyncClient` с тестовым `.env`
- [ ] `test_health.py`: `GET /health` → 200, все поля, `status == "ok"`
- [ ] `test_config.py`: отсутствие обязательной переменной → ValidationError при загрузке Settings
- [ ] Настроить `pytest.ini` или секцию в `pyproject.toml` (`asyncio_mode = auto`)
- [ ] Убедиться, что `make test-backend` вызывает pytest
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все тесты зелёные | `make test-backend` |
| 2 | Health-тест проверяет схему ответа | pytest -v |
| 3 | Config-тест изолирован от реального `.env` | monkeypatch / tmp env |
| 4 | Lint проходит | `uv run ruff check backend/tests/` |
| 5 | `make ci` проходит | `make ci` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `backend/tests/conftest.py` — фикстуры
- `backend/tests/test_health.py` — smoke health
- `backend/tests/test_config.py` — fail-fast config
- `backend/pyproject.toml` — pytest config (изменение)

---

## Scope

**Трогаем:** только файлы из списка «Артефакты» + `Makefile`/`make.ps1` только если `test-backend` ещё не подключён.

**НЕ трогаем:**
- Бизнес-логика agent/RAG/tools (sprint-02)
- frontend тесты
- docker-compose

---

## Риски и допущения

- Допущение: тесты не требуют реального OpenRouter/Langfuse — мок env в conftest.
- Риск: глобальный singleton `get_settings()` кэширует config — в тестах сброс кэша или `lru_cache.clear()`.

---

## Открытые вопросы

- [ ] Нет блокирующих
