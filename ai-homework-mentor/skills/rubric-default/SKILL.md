---
name: rubric-default
description: >
  Mentors reviewing general homework submissions against baseline criteria
  (requirements, structure, completeness). Use when topic has no specialized rubric.
---

# Rubric: General Homework

Instructions for a **mentor reviewing student work** — not for answering the student directly.

## What we check

| Criterion id | Required | Look for |
|--------------|----------|----------|
| `requirements` | yes | Stated assignment goals are met in the submitted files |
| `structure` | yes | Code is organized, readable, maintainable |
| `completeness` | yes | Required files and entry points are present |

## Review checklist

1. Read `/rubric/active.yaml` and the brief file list.
2. For each criterion above, note **pass / partial / fail** with a concrete file reference.
3. Prefer evidence over opinion; do not invent missing requirements.
4. Never execute student code; never read `.env` or secrets.
5. Write the full note to the assigned `/notes/` path; return only a short summary upstream.

## Required vs optional

- **Required:** `requirements`, `structure`, `completeness` — gaps here are blocking issues.
- **Optional:** none in this rubric.

## Out of scope

- Framework-specific API patterns (see ecosystem skills when routed).
- Deep style tooling (see `modern-python` when routed for code quality).
