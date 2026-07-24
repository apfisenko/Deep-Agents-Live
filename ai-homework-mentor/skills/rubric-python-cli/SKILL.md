---
name: rubric-python-cli
description: >
  Mentors reviewing Python CLI homework against entry point, packaging, docs,
  and quality criteria. Use when assignment topic is python-cli or similar.
---

# Rubric: Python CLI Homework

Instructions for a **mentor reviewing a Python CLI submission** — not for rewriting the student app.

## What we check

| Criterion id | Required | Look for |
|--------------|----------|----------|
| `cli-entry` | yes | Clear CLI entry point and argument handling |
| `packaging` | yes | Layout follows Python packaging conventions (`src/` or clear modules) |
| `docs` | no | README or docstrings explain how to run the CLI |
| `quality` | yes | Style and error handling are reasonable for a small CLI |

## Review checklist

1. Read `/rubric/active.yaml` and files from the brief.
2. Locate the entry point (`__main__`, console script, or documented `main`).
3. Judge packaging: importable modules vs one-off scripts.
4. Docs are optional — note absence as improvement, not a hard fail.
5. Quality: focus on clarity and error handling; defer deep tooling to `modern-python` if attached.
6. Never execute student code; never open `.env` or API keys.
7. Full note → `/notes/`; short summary → parent only.

## Required vs optional

- **Required (blocking):** `cli-entry`, `packaging`, `quality`
- **Optional:** `docs`

## Out of scope

- FastAPI/REST layout (use `fastapi-templates` only when API is detected).
- Full product synthesis / fix_plan (orchestrator / later sprint).
