# Handoff contract (S4) — примеры

Контракт: `ReviewBrief` → изолированный reviewer → `notes/review_<aspect>.md` + `ReviewSummary` наверх.

Родитель хранит **summary + note_path**, не полный текст ноты.

---

## ReviewBrief (task tool `description`)

```json
{
  "aspect": "architecture",
  "goal": "Check module layout, packaging, and CLI entry for a Python homework repo.",
  "file_paths": [
    "/code/README.md",
    "/code/pyproject.toml",
    "/code/src/hw/__init__.py",
    "/code/src/hw/cli.py"
  ],
  "rubric_criterion_ids": ["packaging", "cli-entry", "structure"],
  "constraints": [
    "Do not review style or error-handling quality (code_quality reviewer).",
    "Use workspace paths only; do not paste file contents into the brief."
  ]
}
```

В промпте оркестратора brief передаётся как текст `description` у `task(subagent_type=reviewer_architecture, ...)`.

---

## Review note (файл субагента)

Путь: `/notes/review_architecture.md`

```markdown
# Architecture review

## Summary
Clear package layout under `src/hw/`; CLI entry documented in README.

## Findings
- **packaging**: `pyproject.toml` declares `[project.scripts]` entry point.
- **structure**: modules split by concern; no circular imports observed.
- **cli-entry**: `hw.cli:main` matches README usage example.

## Evidence
- `/code/pyproject.toml` lines 12–15
- `/code/README.md` «Usage» section
```

Полная нота остаётся в workspace; в контекст родителя не попадает.

---

## ReviewSummary (ответ субагента родителю)

```json
{
  "aspect": "architecture",
  "findings": [
    "Package layout under src/hw/ is coherent; entry point declared in pyproject.toml.",
    "README documents CLI usage consistent with scripts entry."
  ],
  "criterion_ids": ["packaging", "cli-entry", "structure"],
  "risks": [],
  "open_questions": [],
  "note_path": "/notes/review_architecture.md"
}
```

Лимиты (см. `reviewers/schemas.py`):

- findings: 1–5 пунктов, ≤200 символов каждый
- суммарный бюджет findings: ≤1200 символов (обрезка, не ошибка)
- risks / open_questions: до 3 пунктов

---

## Правило изоляции

| Слой | Что видит |
|------|-----------|
| Reviewer subagent | brief + файлы из brief + rubric slice |
| Parent orchestrator | summaries + `note_path` (+ пути в workspace) |
| Verbose CLI | brief (сжато) → summary → note path; CE-лента родителя |
