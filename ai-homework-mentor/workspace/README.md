# Workspace sessions (local)

Runtime review artifacts live under `workspace/<session_id>/` and are **gitignored**.

Each run creates:

- `input/submission.json`
- `code/` — staged student code
- `rubric/active.yaml`
- `plan/todo.json` — optional todo snapshot
- `notes/` — reviewer notes
- `output/feedback.json` and `output/feedback.md`

Do not commit session directories.
