# Summary: dict-subagent

**Sprint:** 03-course-qa
**Task:** 02-dict-subagent
**Статус:** ✅ Done
**Дата:** 2026-08-02

---

## Что сделано

Реализован `src/course_companion/subagents/course_qa.py` — DeclarativeSubAgent с двумя тулами и dict-спекой.

### Ключевые решения

**`KB_DIR` от `__file__`, не от `cwd`:**
```python
KB_DIR = Path(__file__).parent.parent.parent.parent / "data" / "kb"
```
Путь абсолютный, не зависит от рабочей директории запуска — проверено пользователем.

**Path-traversal защита — до `resolve()`:**
Блокировка по символам `/`, `\\`, `..` в имени файла ещё до формирования пути. Файл физически не открывается.

**EM102/TRY003 (ruff):**
Исключения с f-строками в сообщении требуют промежуточной переменной:
```python
msg = f"Access denied: {filename}"
raise PermissionError(msg)
```

## Артефакты

- `src/course_companion/subagents/course_qa.py`
- `tests/subagents/test_course_qa.py`

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | 4 теста проходят | ✅ 4/4 passed |
| 2 | `pytest.raises(PermissionError)` в тесте | ✅ |
| 3 | ruff чист | ✅ |
| 4 | mypy чист | ✅ |
| 5 | path-traversal не читает файл | ✅ подтверждено пользователем |
| 6 | Путь не зависит от cwd | ✅ подтверждено пользователем |

## Итог полного прогона

```
9 passed in 1.49s
```
(4 новых теста course-qa + 3 homework-checker + 2 smoke)
