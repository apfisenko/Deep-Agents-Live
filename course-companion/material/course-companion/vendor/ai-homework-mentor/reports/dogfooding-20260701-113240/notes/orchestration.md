# Review: orchestration — Subagents and delegation

## Проверенные файлы

- `/code/mentor/agent/reviewers.py` — `build_reviewer_subagents()`, `parse_task_messages()`, `build_delegation_user_message()`
- `/code/mentor/agent/orchestrator.py` — `MentorOrchestrator.run()`, `RunResult.delegation_warning`
- `/code/config/prompts/orchestrator.yaml` — system prompt для оркестратора
- `/code/config/rubrics/deep-agents.yaml` — список аспектов (5 штук)
- `/code/mentor/agent/tools/rubric.py` — `Rubric` dataclass

---

## Критерий 1: Reviewer subagents per rubric aspect

**Статус: ВЫПОЛНЕНО** ✅

- `build_reviewer_subagents()` (reviewers.py:50–87) итерирует `rubric.aspects` и для каждого создаёт subagent с именем `reviewer-{aspect_id}`.
- Каждый subagent получает:
  - `name` = `reviewer-{aspect_id}` (напр. `reviewer-orchestration`)
  - `description` = `"Review rubric aspect '{title}' ({aspect_id}) in student code"`
  - `system_prompt` — содержит aspect id, title, criteria, rubric skill, public skills, инструкцию записать `/notes/{aspect_id}.md`
  - `skills` = пути из `skill_plan.virtual_paths_for_aspect(aspect_id)`
- В rubrics/deep-agents.yaml 5 аспектов → создаётся 5 subagent'ов.
- В orchestrator.py:195 subagents передаются в `create_deep_agent(subagents=subagents)`.
- Вспомогательные функции: `reviewer_name(aspect_id)` возвращает `reviewer-{id}`, `aspect_id_from_name(name)` обратное преобразование.

---

## Критерий 2: Delegation only via task tool

**Статус: ВЫПОЛНЕНО** ✅

- **System prompt** (orchestrator.yaml:15): *"Do NOT review code yourself — always delegate via task to reviewer subagents."*
- **delegation_user_message** (reviewers.py:211): *"Do NOT review code yourself — delegate every aspect via task."*
- **parse_task_messages()** (reviewers.py:111–146):
  - Парсит только `AIMessage.tool_calls` (строчки 121–123).
  - Фильтрует по `name == "task"` (строка 125–126).
  - Проверяет `subagent_type.startswith("reviewer-")` (строка 130–131).
  - Извлекает `tool_call_id` и находит соответствующий `ToolMessage` с результатом.
  - Определяет `status` как `"done"` или `"error"`.
- **Delegation warning** (orchestrator.py:243–249): если `len(subagent_runs) < len(rubric.aspects)`, генерируется предупреждение.
- **`build_delegation_user_message()`** (reviewers.py:178–213) перечисляет всех доступных reviewer-сабагентов в конце сообщения, чтобы оркестратор знал, кому делегировать.

---

## Критерий 3: write_todos plan before delegation

**Статус: ВЫПОЛНЕНО** ✅

- **System prompt** (orchestrator.yaml:6): *"Use write_todos to plan review (one item per rubric aspect)."*
- **delegation_user_message** (reviewers.py:199–200): шаг 1 workflow — *"Use write_todos — one item per rubric aspect."*
- После write_todos, workflow предписывает:
  1. Написать brief в `/notes/brief-{aspect-id}.md`.
  2. Делегировать через `task(subagent_type="reviewer-{aspect-id}", description="...")`.
  3. Собрать результаты в `/output/feedback.md`.

---

## Дополнительные находки

1. **Enrichment после парсинга** (reviewers.py:149–175): `enrich_subagent_runs()` добавляет `skills_applied` и `skills_confirmed` из `SkillPlan` и `ContextTracker` — хорошая observability.
2. **Stateless subagents**: в brief и system prompt явно указано, что subagents stateless, вся информация передаётся в `description` — соответствует best practice из deep-agents-orchestration SKILL.md.
3. **workspace.plan_path** (orchestrator.py:185–191): создаётся review plan с чеклистом аспектов — дополнительная гарантия, что оркестратор видит все аспекты.

---

## Итог по критериям

| Критерий | Статус |
|---|---|
| Reviewer subagents per rubric aspect | ✅ Выполнено |
| Delegation only via task tool | ✅ Выполнено |
| write_todos plan before delegation | ✅ Выполнено |
