# Боль Sprint 03 — одному агенту тесно

> Зафиксировано для контраста с S4 (изоляция reviewer-субагентов).
> **Источники:** B = `tests/fixtures/large_hw` (CI), A = [pallets/click](https://github.com/pallets/click) @ 8.2.1 (demo).

---

## Тезис

Даже с суммаризацией и offload в файлы **один** review-агент на большом репозитории:

- раздувает контекст по шагам;
- теряет «обзорность» проверки;
- требует CE-срабатываний, которые видны, но **не** делают процесс лёгким.

**Вывод:** нужна изоляция аспектов (S4), а не «ещё больше сжатия».

---

## Метрики (CI fixture `large_hw`, порог CE занижен для демонстрации)

| Метрика | Значение (пример прогона) |
|---------|---------------------------|
| Файлов в staging | ~61 |
| Шагов context trace | 4+ |
| Max tokens (estimate) | ~980 → ~340 после summarize |
| Summarize events | 1 |
| Offload events | 1 (`/conversation_history/...`) |
| Субагенты | 0 |

Пороги для демо-прогона (не production):

```yaml
context:
  summarize_threshold_tokens: 128
  offload_threshold_tokens: 64
```

Production defaults в `config/agent.yaml`: `summarize_threshold_tokens: 0` → model-aware defaults DeepAgents.

---

## Фрагмент verbose (маскированный)

```text
┌─ context engineering ─────────────────────────────┐
│ step │ tokens │   Δ │ source      │ event     │ … │
│ 0    │    420 │  +0 │ estimate    │ none      │   │
│ 1    │    980 │ +560│ estimate    │ none      │   │
│ 2    │    310 │ -670│ model_usage │ summarize │   │
│ 3    │    340 │  +30│ model_usage │ offload   │ … │
└───────────────────────────────────────────────────┘
┌─ CE events ───────────────────────────────────────┐
│ summarize @ step 2                                │
│ offload @ step 3 → /conversation_history/thread.md│
└───────────────────────────────────────────────────┘
```

---

## Live demo (variant A)

```powershell
cd ai-homework-mentor
.\make.ps1 run -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli" -Verbose
# или GitHub (сеть):
.\make.ps1 run -- -Message "https://github.com/pallets/click Тема: python-cli" -Verbose
```

---

## Качественное ощущение

- Агент «видит» много файлов, но проверка становится **мутной**: приходится сжимать историю, теряя детали.
- CE помогает не упасть по лимиту, но **не** заменяет декомпозицию по аспектам.

См. заготовку сравнения: [contrast-s3-s4.md](./contrast-s3-s4.md).
