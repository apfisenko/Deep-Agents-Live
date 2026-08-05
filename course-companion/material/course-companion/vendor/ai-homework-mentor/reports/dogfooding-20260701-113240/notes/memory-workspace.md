# memory-workspace — Результаты ревью

**Дата:** 2025-05-19

## Проверенные критерии

### ✅ 1. Чёткая структура рабочей директории (clear workspace layout)

- **`Workspace`** (`/code/mentor/agent/tools/workspace.py`) — dataclass с имущественными путями:
  - `code/`, `notes/`, `output/`, `skills/` — четыре основные директории
  - Плюс метафайлы: `submission.md`, `plan.md`, `rubric.md`, `code-index.md`
  - Внутри `output/`: `feedback.md`, `final_feedback.md`, `fix_plan.md`, `report.md`
- **`ensure_layout()`** (строка 65–68) создаёт только `code/`, `notes/`, `output/`.
  - ⚠️ `skills/` не создаётся в `ensure_layout()`, а создаётся лениво внутри `materialize_workspace_skills()`.
- **`WorkspaceManager.create(seed)`** (строка 87–94) генерирует уникальную директорию: `{YYYYMMDD-HHMMSS}-{sha256[:12]}`.
  - Коллизии практически исключены благодаря timestamp + хэшу seed (source+topic).
- **Найден по**: rubric-deep-agents (аспект memory-workspace).

### ✅ 2. Skills и rubric материализованы под /skills/ в workspace

- **`materialize_workspace_skills()`** (`/code/mentor/agent/tools/skills_loader.py`, строка 141–173):
  - Копирует rubric SKILL.md → `workspace/skills/<rubric_skill>/SKILL.md`
  - Копирует public SKILL.md → `workspace/skills/<skill_name>/SKILL.md` (каждый уникальный скилл один раз)
  - Создаёт `workspace/skills/manifest.md` со списком всех скиллов по аспектам
- В оркестраторе (строка 177) вызывается `materialize_workspace_skills()` сразу после `acquire_code()`.
- **`SkillsPlan.virtual_paths_for_aspect()`** (строка 54–62) генерирует виртуальные пути вида `/skills/<name>` для DeepAgents middleware.
- **Найден по**: rubric-deep-agents + deep-agents-memory (раздел про FilesystemBackend).

### ⚠️ 3. Защита от секретов (secrets — .env)

- **`SKIP_DIRS`** (`/code/mentor/agent/tools/parse.py`, строка 17–25):
  - Содержит: `.git`, `__pycache__`, `.venv`, `node_modules`, `.ruff_cache`, `.pytest_cache`, `.mentor-workspace`
  - ❌ **`.env` отсутствует в `SKIP_DIRS`**
- **`_is_text_file()`** (строка 115–120): `.env` имеет суффикс `.env`, который **не входит** в `TEXT_EXTENSIONS`.
  - ✅ Это значит, что `.env` не будет включён в `_iter_code_files()` и `build_code_index()`.
  - ⚠️ Однако `copy_local_directory()` (строка 144–153) использует `shutil.ignore_patterns(*SKIP_DIRS, "*.pyc")`.
    - `.env` **НЕ** входит в эти паттерны игнорирования → файл будет физически скопирован в workspace.
- **Риск**: Если студент запушил `.env` в репозиторий, файл попадёт в `workspace/code/`, хотя не будет проиндексирован.
- **Рекомендация**: добавить `".env"` в `SKIP_DIRS` или добавить `".env"` в `ignore_patterns` в `copy_local_directory()`.
- **`.env.example`** — корректно включён в `TEXT_EXTENSIONS` (строка 35).
- **Найден по**: rubric-deep-agents (аспект memory-workspace — "no secrets in workspace").

### ✅ 4. Code-index offloaded в workspace

- **Оркестратор** (`/code/mentor/agent/orchestrator.py`, строки 168–170):
  ```python
  code_index = build_code_index(workspace.code_dir)
  workspace.write_text(workspace.code_index_path, code_index)
  tracker.record_offload("/code-index.md", max(len(code_index) // 4, 1))
  ```
- ✅ Индекс записывается в `workspace/code-index.md` и регистрируется через `tracker.record_offload()` с подсчётом сэкономленных токенов.
- ✅ Это позволяет держать контекст оркестратора компактным, не загружая туда весь список файлов.
- **Найден по**: rubric-deep-agents (аспект memory-workspace — "Code index offload").

---

## Итоговая таблица

| Критерий | Статус | Замечания |
|----------|--------|-----------|
| Session workspace layout (code, notes, output, skills) | ✅ | `ensure_layout()` не создаёт `skills/`, но он создаётся позже |
| Unique session dir (timestamp+hash) | ✅ | `WorkspaceManager.create()` |
| Skills materialized under /skills/ | ✅ | SKILL.md + manifest |
| Code-index offloaded to workspace | ✅ | `tracker.record_offload()` |
| No secrets — .env excluded from copy | ⚠️ | Не в `SKIP_DIRS`, не в `ignore_patterns`, но скрыт из индекса |
| No secrets — .env excluded from index | ✅ | _is_text_file() фильтрует |

## Файлы (источники)

- `/code/mentor/agent/tools/workspace.py` — Workspace, WorkspaceManager, ensure_layout()
- `/code/mentor/agent/tools/skills_loader.py` — materialize_workspace_skills(), SkillPlan
- `/code/mentor/agent/orchestrator.py` — workspace lifecycle, code-index offload
- `/code/mentor/agent/tools/parse.py` — SKIP_DIRS, _is_text_file(), copy_local_directory()
- `/skills/deep-agents-memory/SKILL.md` — FilesystemBackend / virtual paths
- `/skills/rubric-deep-agents/SKILL.md` — rubric criteria for memory-workspace
