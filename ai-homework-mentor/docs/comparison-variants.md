# Итоговый отчёт: варианты проверки и контекст/токены

> **Дата:** 2026-07-24  
> **Источник кода:** `tests/fixtures/large_hw` (~61–62 файла), тема `python-cli`  
> **Модель live:** `openrouter:openai/gpt-4o-mini`  
> **Связанные артефакты:** [pain-s3.md](./pain-s3.md), [contrast-s3-s4.md](./contrast-s3-s4.md), [skills-inventory-s5.md](./skills-inventory-s5.md), `logs/summary_log_*.md`  
> **S8 ✅** (2026-07-25): воспроизводимое сравнение режимов — [`../sprints/sprint-08-review-modes/README.md`](../sprints/sprint-08-review-modes/README.md); отчёты на **русском**, compare/review — только в `docs/`

**Что измеряем:** размер **родительского** контекста (estimate / `usage_metadata`), CE-события, артефакты — не полный bill OpenRouter по всем окнам.

---

## 1. Варианты (слои продукта)

| ID | Слой | Как работает | Статус |
|----|------|--------------|--------|
| **V0 / S2** | Single-agent E2E | Один агент: plan → review → простой feedback | ✅ база |
| **V1 / S3** | Single-agent + CE | То же на большом репо; видны summarize/offload | ✅ «боль» |
| **V2 / S4** | + Reviewer subagents | Родитель делегирует 2 аспекта; notes в FS | ✅ |
| **V3 / S5** | + Skills routing | В brief — rubric + `modern-python` / опц. fastapi | ✅ |
| **V4 / S6** | + Synthesis | Reflection → `final_feedback` / `fix_plan` | ✅ |
| **V5 / S8** | Флаг режима + отчёты | `-Mode single\|subagents`; run/compare в `docs/` (RU); токены окон reviewers | ✅ |
| **V6 / S9** | Checkpoint / resume | долгие сессии, продолжение | 📋 план |
| **V7 / S10** | + Dynamic models | Cheap reviewers / strong synthesis | 📋 план |

Текущий CLI = **V5** (**S8 ✅**): режимы + русские run/compare/review-отчёты в `docs/`.

---

## 2. Сводная таблица (главное)

| Метрика | V1 / S3 | V2–V4 / S4–S6 (live) |
|---------|---------|----------------------|
| Окон LLM на review | 1 | 1 parent + 2 reviewers |
| Max **parent** tokens | ~980 → ~340 после CE* | ~2145–2509 |
| Summarize (parent) | 1* | 0 (prod thresholds) |
| Offload (parent) | 1* | 0 |
| Review notes | 1 общий поток | 2 файла: architecture + code_quality |
| Handoffs | 0 | 2 |
| Skills в brief | нет | rubric + ecosystem (S5) |
| «Мутность» проверки | высокая (сжатие истории) | ниже (аспекты изолированы) |
| Полный текст review в parent | да (пока не срежет CE) | нет — только summary + path |

\*S3: CI/демо с **заниженными** порогами (`summarize_threshold_tokens: 128`, `offload_threshold_tokens: 64`). Не сравнивать 980 и 2509 как «S4 хуже».

### Live S4/S5 (один fixture)

| Session log | Parent max (est.) |
|-------------|-------------------|
| `logs/summary_log_20260724T173923Z.md` | 2230 |
| `logs/summary_log_20260724T180043Z.md` | 2145 |
| `logs/summary_log_20260724T180637Z.md` | 2201 |
| `logs/summary_log_20260724T183353Z.md` (S5 + skills) | 2509 |

Рост parent в S5 (~+300 vs ранний S4) типичен: в thread копятся summaries + skill-маршрутизация; **полные notes** по-прежнему в `/notes/`.

---

## 3. Поведение по вариантам

### V1 / S3 — «одному агенту тесно»

- Один поток читает много файлов → окно пухнет.
- CE спасает от лимита (summarize/offload), но детали теряются.
- Verbose: лента CE, нет panel `subagents`.
- Док: [pain-s3.md](./pain-s3.md)

**Экономия токенов:** вынужденное сжатие окна (не декомпозиция).  
**Цена:** качество/обзорность review.

### V2 / S4 — изоляция аспектов

- Parent: plan + `task` → brief → ждёт summary.
- Тяжёлое чтение кода — в отдельных окнах reviewers.
- Verbose: CE + `subagents` + `parent max context`.
- Док: [contrast-s3-s4.md](./contrast-s3-s4.md)

**Экономия:** не parent bill целиком, а **не тащить полные notes в окно оркестратора**.  
**Цена:** суммарно больше LLM-вызовов (2 reviewer + parent); parent max может быть выше, чем демо-S3.

### V3 / S5 — skills

- Процедуры в SKILL.md, не дублируются целиком в системном промпте.
- Verbose: блок Rubric & Skills.
- Инвентарь: [skills-inventory-s5.md](./skills-inventory-s5.md)

**Экономия:** повторное использование процедур без раздувания промпта.  
**Цена:** чуть больше контекста на маршрутизацию/brief.

### V4 / S6 — синтез

- Склеивает notes → reflection → структурированный итог студенту.
- На parent-токены влияет слабо (читает артефакты из FS); добавляет вызовы synthesis/reflection.

### V5 / S8 — режимы и отчёты

- CLI `-Mode single|subagents` воспроизводит контраст V1 vs V2–V4 без ручной смены кода.
- Run-отчёт (RU) в `docs/`: параметры, **шаги parent**, таблица **токенов окон reviewers**, totals, время.
- Важно: шаги CE = только parent; нагрузка субагентов — в секции «Токены субагентов» (не в parent-trace).
- `compare-modes` → только `docs/compare-modes-*.md` (таблица + плюсы/минусы на русском).

### V6 / S9 — checkpoint

- Долгие сессии и resume — см. [`../sprints/sprint-09-checkpoint-resume/README.md`](../sprints/sprint-09-checkpoint-resume/README.md).

### V7 / S10 — стоимость ($)

- Цель: дешёвая модель на reviewers, сильная на synthesis.
- Здесь уже про **деньги/latency**, не про изоляцию окна.

---

## 4. Где реально экономим (и где нет)

```text
Что экономим                          Что НЕ экономим автоматически
─────────────────────────────────     ────────────────────────────────
✓ Засорение parent полными notes      ✗ Суммарный token bill всех окон
✓ Потерю деталей от forced summarize  ✗ Число LLM-вызовов (S4 их больше)
✓ Дубли процедур в промпте (skills)   ✗ Parent max estimate vs демо-S3
                                      → S10: $/токен по ролям
```

**Вывод roadmap:** CE удерживает окно → субагенты разгружают родителя → skills не раздувают промпт → S8 делает контраст воспроизводимым (и меряет окна reviewers) → S9 resume → S10 режет стоимость.

---

## 5. Качество результата (не только токены)

| | S3 / mode=single | S4–S6 / mode=subagents |
|--|------------------|------------------------|
| Покрытие аспектов | один смешанный поток | architecture + code_quality явно |
| Артефакты | общий note / feedback | 2 review notes + aggregate feedback |
| Воспроизводимость разбора | низкая после CE | notes на диске, handoff contract |
| Урок для демо | «тесно» | «изоляция закрывает боль» |

---

## 6. Как воспроизвести сравнение

```powershell
cd ai-homework-mentor
.\make.ps1 run -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli" -Mode single -Verbose
.\make.ps1 run -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli" -Mode subagents -Verbose
.\make.ps1 compare-modes -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli"
```

Смотреть:

1. `docs/run-report-*.md` — параметры; **рост контекста = parent**; **токены субагентов** по аспектам; totals; время;
2. `docs/compare-modes-*.md` — сравнительная таблица (в т.ч. сумма max окон reviewers) и плюсы/минусы (только `docs/`);
3. в verbose / `logs/summary_log_*.md` — CE и panel subagents.

Исторический прогон S3 без флага: [pain-s3.md](./pain-s3.md).

---

## 7. Рекомендации

1. Для демо контраста показывать **пару**: много parent-шагов в `single` vs короткие parent-шаги + таблица окон reviewers в `subagents`.
2. Метрика успеха изоляции: **notes на диске + короткий summary в parent**, плюс видимые max окон reviewers — не только минимальный parent max.
3. Для $ — ждать S10 + отдельный benchmark; сейчас сравнивать архитектуру контекста, не invoice.
