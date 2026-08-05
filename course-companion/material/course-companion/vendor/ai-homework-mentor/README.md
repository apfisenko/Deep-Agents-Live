# AI Homework Mentor

CLI-утилита для проверки домашних заданий студентов на базе DeepAgents.

## Установка

```bash
cd ai-homework-mentor
make sync
```

Секреты: скопируйте `.env.example` → `.env` или используйте корневой `.env` репозитория (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`).

## Команды

| Команда | Назначение |
|---------|------------|
| `make ci` | lint + pytest |
| `make chat` | S00 smoke: LLM без review |
| `make check-bot-verbose` | Python CLI / Telegram bot |
| `make check-backend-verbose` | FastAPI REST API |
| `make check-docker-verbose` | Docker (devops/) |
| `make check-self-verbose` | Dogfooding: DeepAgents rubric на себе |

Ручной запуск:

```bash
uv run mentor check <path|url> --topic "..." [--verbose]
```

## Skills: как это работает

1. **Rubric YAML** (`config/rubrics/*.yaml`) — `rubric_skill` + `aspect_skills` по аспектам.
2. **Материализация** — SKILL.md копируются в `workspace/skills/` (verbose: таблица **Skills loaded**).
3. **Reviewer subagents** — читают `/skills/...`; verbose показывает **assigned** vs **confirmed read**.
4. **Синтез (S06)** — `output/final_feedback.md`, `fix_plan.md`, `report.md` на русском; каждое замечание с навыком.

## Dogfooding (S07)

Рубрика `deep-agents` проверяет сам проект по навыкам DeepAgents:

```bash
make check-self-verbose
```

Тема: `DeepAgents homework mentor` → `config/rubrics/deep-agents.yaml` + skills: orchestration, core, memory, middleware, modern-python.

Итоговый отчёт: `workspace/.../output/report.md`.

## Ограничения v1

См. [docs/limitations-v1.md](docs/limitations-v1.md).
