# Ограничения v1 — AI Homework Mentor

- Код студента **не исполняется** в sandbox.
- Делегирование через `task` зависит от compliance модели (иногда 0/N subagents).
- Skills **confirmed read** фиксируется только при `read_file`/`ls`/`glob` на `/skills/`.
- Синтез использует LLM; при сбое — детерминированный fallback из заметок.
- Dogfooding на `.` сканирует проект без `.mentor-workspace`, `.venv`, `node_modules`.
- OpenRouter/модель влияют на качество и стабильность feedback.
