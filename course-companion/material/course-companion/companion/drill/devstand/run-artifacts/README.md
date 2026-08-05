# Артефакты живых прогонов стенда (фаза 2C)

Все прогоны — браузером (Playwright) на `localhost:5273`, форма генерируется
живой LLM (OpenRouter, `google/gemini-3.5-flash`); логи `*.log.txt` (суффикс
`.txt` — чтобы пережить `*.log` в корневом `.gitignore`).

| Прогон | Что показывает | Файлы |
|---|---|---|
| 1 | полный round-trip: кейс → LLM-форма (20 сообщений, инкрементальный рендер) → заполнение → userAction с данными формы → доставка-заглушка (enqueue) | `run1-form-generated.png`, `run1-action-delivered.png`, `run1-delivered.json`, `server-run1.log.txt` |
| 2 | повтор round-trip свежей генерацией (стабильность шаблонного промпта: 18 сообщений, retry не понадобился) | `run2-action-delivered.png`, `run2-delivered.json`, `server-run1.log.txt` (тот же сервер) |
| 3 | retry в действии (`DRILL_FAIL_FIRST=1`): попытка 1 неполная → забракована + deleteSurface → попытка 2 живой LLM отдала полную форму | `run3-retry-form-after-failed-attempt.png`, `server-run3-retry.log.txt` |
| 4 | smoke после INV-12-ревью: round-trip + повторная отправка формы (deleteSurface перед ack — клиент не падает на дубле createSurface) | `run4-postreview-resubmit-ok.png`, `run4-delivered.json`, `server-run4-postreview.log.txt` |
